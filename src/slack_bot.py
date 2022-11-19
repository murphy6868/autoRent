# https://andrewlearningnote.com/用python寫出slack機器人/
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackBot:
    # payload sample
    payload = {
        "channel": "",
        "blocks": [

        ],
        "icon_url": "",
    }

    # the constructor of the class. It takes the channel name, slack bot taken, and bot avatar
    # as input parameters.
    def __init__(self, channel, token, bot_icon=None):
        self.channel = channel
        self.token = token
        self.bot_icon = bot_icon
    
    # set the channel
    def __decide_channel(self):
        self.payload["channel"] = self.channel

    # use the input message to change the payload content. this method will remove previous
    # message to prevent duplicate. 
    def decide_message(self, message):
        m = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        message
                    )
                }
            }
        for item in self.payload["blocks"]:
            self.payload["blocks"].remove(item)
        self.payload["blocks"].append(m)

    # use input url of picture to change the payload content.
    # this method will remove previous message to prevent duplicate.
    def decide_picture_as_message(self, pic_url):
        for item in self.payload["blocks"]:
            self.payload["blocks"].remove(item)
        accessory = dict(type="image", image_url=pic_url, alt_text="image")
        self.payload["blocks"].append(accessory)

    # decide slack app's avatar
    def __decide_bot_icon(self, url):
        self.payload["icon_url"] = url

    # craft and return the entire message payload as a dictionary.
    def __get_message_payload(self):
        self.__decide_channel()
        return self.payload

    # use slack api to send message 
    def send_message(self, decide_message):
        slack_web_client = WebClient(self.token)
        self.decide_message(decide_message)
        self.__decide_bot_icon(self.bot_icon)
        message = self.__get_message_payload()
        slack_web_client.chat_postMessage(**message)

    # use slack api to send picture's url as picture message
    def send_picture_as_message(self, decide_picture_as_message):
        slack_web_client = WebClient(self.token)
        self.__decide_bot_icon(self.bot_icon)
        self.decide_picture_as_message(decide_picture_as_message)
        message = self.__get_message_payload()
        slack_web_client.chat_postMessage(**message)

    # determine file location and send as message 
    def send_file(self, file_location):
        slack_web_client = WebClient(self.token)
        try:
            response = slack_web_client.files_upload(
                channels=[self.channel],
                file=file_location
            )
            assert response["file"]  # the uploaded file
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")
            print(self.channel)