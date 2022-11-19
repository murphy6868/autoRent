from flask import Flask, request, Response
from threading import Thread
import slack_sdk as slack
import os
from pathlib import Path
import sys
sys.path.append('src')
sys.path.append('src/slack_bot_server')
import utils

token = utils.getCredentials().slackBotOAuthToken

client = slack.WebClient(token=token)

app = Flask('')
from command_api import command_api_bp
from action_endpoint import action_endpoint_bp
app.register_blueprint(command_api_bp, url_prefix='/command')
app.register_blueprint(action_endpoint_bp)

@app.route('/')
def home():
  return "The bot is alive!!"


def run():
  app.run(host='0.0.0.0', port=8443)


def keep_alive():
  t = Thread(target=run)
  t.start()
