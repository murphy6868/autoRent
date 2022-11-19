from slack_bot import SlackBot
import utils
from datetime import datetime, timedelta
import requests
requests.packages.urllib3.disable_warnings() 
from bs4 import BeautifulSoup
import sso_helper, utils
import qrcode, tempfile, time, sys
import logging, log_utils
L = log_utils.createLogger(__name__, logging.DEBUG)

WEEK_DAY_MAP = ['(一)', '(二)', '(三)', '(四)', '(五)', '(六)', '(日)']
def getOrderStatus(TOS, TPS, sess=utils.createSession(proxy=utils.TOR_PROXY)):
    ssoHelper = sso_helper.SsoHelper(utils.getCredentials())
    tasks = utils.getRentTasks()
    ssoHelper.login(sess, datetime.strptime(tasks[0]['date'], "%Y.%m.%d"))
    pageNum = 0
    ordersInfo = []
    baseURL = f"https://rent.pe.ntu.edu.tw/member/rental/?TOS={TOS}&TPS={TPS}"
    ordersStr = ""
    while(1):
        pageNum += 1
        URL = f"{baseURL}&Page={pageNum}"
        PARAMS = {}
        res = sess.get(url = URL, params = PARAMS)
        soup = BeautifulSoup(res.content, "html.parser")
        tbodies = soup.find_all("tbody")
        if len(tbodies) == 0:
            break
        for tbody in tbodies:
            OrderNo = tbody.find("div", {"class": "MC OrderNo"}).text
            CreateDate = tbody.find("div", {"class": "CreateDate"}).text
            RD = tbody.find("span", {"class": "RD"}).text 
            RT = tbody.find("span", {"class": "RT"}).text.replace(':00', '').replace('、', ',').replace(' ~ ', '~')
            TotalAmount = tbody.find("div", {"class": "MC TotalAmount"}).text
            L.info([OrderNo, CreateDate, RD, RT, TotalAmount])
            #ordersInfo.append([OrderNo, RD, RT, TotalAmount])
            ordersInfo.append({ 'OrderNo':OrderNo,
                                'RD':RD,
                                'RD_WEEKDAY':WEEK_DAY_MAP[datetime.strptime(RD, '%Y-%m-%d').weekday()],
                                'RT':RT,
                                'TotalAmount':TotalAmount})
            ordersStr += '\n' + " ".join([OrderNo, CreateDate, RD, RT, TotalAmount])
            if datetime.now() > datetime.strptime(RD,'%Y-%m-%d') + timedelta(days=1):
                break
    L.debug(f"TOS={TOS} && TPS={TPS}{ordersStr}")
    return ordersInfo

def formatRDRTmessage(RDRT_map, RDRT_tup, add_edit_link=False):
    RD = RDRT_tup[0][5:].replace('-','/')
    RD_WEEKDAY = RDRT_tup[2]
    RT = f"{RDRT_tup[1].count('~')}小({RDRT_tup[1]})" 
    for i in range(9,22):
        RT = RT.replace(f"~{i},{i}~", '~')
    message = f"\u2022 {RD}{RD_WEEKDAY}  {RT}\n"
    for RDRT_info in RDRT_map[RDRT_tup]:
        message += f"     - {RDRT_info['OrderNo']} {RDRT_info['TotalAmount']}"
        if add_edit_link:
            message = message.replace(RDRT_info['OrderNo'], f"<https://rent.pe.ntu.edu.tw/order/?Edit=O:{int(RDRT_info['OrderNo'][-5:]) + 24} | {RDRT_info['OrderNo']}>")
        message += '\n'
    return message

def sendUnpaidOrder():
    token = utils.getCredentials().slackBotOAuthToken
    sess = utils.createSession(proxy=utils.TOR_PROXY)
    ordersInfo = getOrderStatus("已核准", "待繳費", sess)

    slack_bot = SlackBot("待繳費", token)
    slack_bot.send_message('='*27)
    
    RDRT_map = {}
    for orderInfo in ordersInfo:
        if datetime.now() > datetime.strptime(orderInfo['RD'],'%Y-%m-%d') + timedelta(days=1):
            break
        RDRT_tup = (orderInfo['RD'], orderInfo['RT'], orderInfo['RD_WEEKDAY'])
        if RDRT_tup not in RDRT_map:
            RDRT_map[RDRT_tup] = []
        RDRT_map[RDRT_tup].append({'OrderNo':orderInfo['OrderNo'], 'TotalAmount':orderInfo['TotalAmount']})

    for RDRT_tup in RDRT_map:
        message = formatRDRTmessage(RDRT_map, RDRT_tup, add_edit_link=True)
        slack_bot.send_message(message)

    return


def sendQRCode():
    token = utils.getCredentials().slackBotOAuthToken
    sess = utils.createSession(proxy=utils.TOR_PROXY)
    ordersInfo = getOrderStatus("已核准", "已繳費", sess)

    slack_bot = SlackBot("qrcode", token)
    slack_bot.send_message('='*27)

    RDRT_map = {}
    for orderInfo in ordersInfo:
        print(orderInfo)
        if datetime.now() > datetime.strptime(orderInfo['RD'],'%Y-%m-%d') + timedelta(days=1):
            break
            #pass
        RDRT_tup = (orderInfo['RD'], orderInfo['RT'], orderInfo['RD_WEEKDAY'])
        if RDRT_tup not in RDRT_map:
            RDRT_map[RDRT_tup] = []
        RDRT_map[RDRT_tup].append({'OrderNo':orderInfo['OrderNo'], 'TotalAmount':orderInfo['TotalAmount']})
        # message = f"{orderInfo}"
        # picture_as_message = f"https://rent.pe.ntu.edu.tw/_/f/qrcode.php?Q={orderInfo['OrderNo']}"
        # slack_bot.send_message(message)
        # slack_bot.send_picture_as_message(picture_as_message)

        # f"https://rent.pe.ntu.edu.tw/_/f/qrcode.php?Q=OA20221104010591"
    tempDir = tempfile.TemporaryDirectory()
    for RDRT_tup in RDRT_map:
        message = formatRDRTmessage(RDRT_map, RDRT_tup)
        slack_bot.send_message(message)
        #slack_bot.send_message(RDRT)
        # for RDRT_info in RDRT_map[RDRT]:
        #     message = formatRDRTmessage(RDRT_map, RDRT)
        #     slack_bot.send_message(message)
        for RDRT_info in RDRT_map[RDRT_tup]:
            qr = qrcode.QRCode(version=1, box_size=10, border=1)
            qr.add_data(RDRT_info['OrderNo'])
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')
            tempFileName = '/'.join([tempDir.name, RDRT_info['OrderNo']])
            img.save(tempFileName)
            #slack_bot.send_file(tempFileName)
            slack_bot.send_message(f"https://rent.pe.ntu.edu.tw/_/f/qrcode.php?Q={RDRT_info['OrderNo']}")
    tempDir.cleanup()
    return

    message = "any message"
    bot_icon = "https://cdn3.iconfinder.com/data/icons/chat-bot-emoji-blue-filled-color/300/14134081Untitled-3-512.png"
    picture_as_message = "http://airbnb.io/img/projects/airflow3.png"
    slack_bot = SlackBot("#qrcode", token, bot_icon)

    #example
    slack_bot.send_picture_as_message(picture_as_message)
    slack_bot.send_message(message)
    filepath = "test.txt"
    slack_bot.send_file(filepath)
    
def cancelOrder():
    # https://rent.pe.ntu.edu.tw/order/?Cancel=O:12134&S=rental
    return

def editOrder():
    # https://rent.pe.ntu.edu.tw/order/?Edit=O:12326
    return

if __name__ == '__main__':
    if sys.argv[1] == 'sendUnpaidOrder':
        sendUnpaidOrder()
    elif sys.argv[1] == 'sendQRCode':
        sendQRCode()
    