from flask import Blueprint
from flask import request, Response
import slack_sdk as slack
import os, time
from pathlib import Path
import sys, subprocess, multiprocessing, shlex, fcntl
sys.path.append('src')
import utils, slack_bot_utils
import logging, log_utils
L = log_utils.createLogger(__name__, logging.DEBUG)

token = utils.getCredentials().slackBotOAuthToken

client = slack.WebClient(token=token)

command_api_bp = Blueprint('command_api', __name__)

@command_api_bp.route('/hello', methods=['GET'])
def helloCommand_GET():
    L.info(f"from: {request.remote_addr}")
    return Response(), 200

@command_api_bp.route('/hello', methods=['POST'])
def helloCommand():
    data = request.form
    print('data', data)
    channel_id = data.get('channel_id')
    client.chat_postMessage(channel=channel_id, text="Hello Command!")
    user_id = data.get('user_id')
    print(user_id)
    client.chat_postMessage(channel=user_id, text="recv /hello")
    
    
    return Response(), 200

def logSenderService(CMD):
    L.debug('logSenderService')
    CMD = shlex.split(CMD)
    client.chat_postMessage(channel='command-log', text=f"=== Executing command: {CMD[-1]} ===")
    p = subprocess.Popen(CMD, stdout=subprocess.PIPE, bufsize=2) # stdin=subprocess.PIPE, stderr=subprocess.PIPE, 
    while True:
        output = p.stdout.readline().decode("utf-8")
        if not output:
            L.info(f"DONE! {CMD}")
            break
        L.debug(output)
        client.chat_postMessage(channel='command-log', text=log_utils.stripColors(output))
    client.chat_postMessage(channel='command-log', text=f"=== Complete executing command: {CMD[-1]} ===")
    return 0

# def multiProcFunction(target, args):
#     p = multiprocessing.Process(target=target, args=args)
#     p.start()

@command_api_bp.route('/get_unpaid', methods=['POST'])
def getUnpaidCommand():
    L.debug('getUnpaidCommand')
    utils.runAsDaemon(logSenderService, ['python src/slack_bot_utils.py sendUnpaidOrder /get_unpaid'])
    data = request.form
    print('data', data)
    channel_id = data.get('channel_id')
    client.chat_postMessage(channel=channel_id, text="Reference #command-log channel for execution progress!")
    user_id = data.get('user_id')
    client.chat_postMessage(channel=user_id, text="recv /get_unpaid")
    return Response(), 200

@command_api_bp.route('/get_qrcode', methods=['POST'])
def getQrcodeCommand():
    L.debug('getQrcodeCommand')
    utils.runAsDaemon(logSenderService, ['python src/slack_bot_utils.py sendQRCode /get_qrcode'])
    data = request.form
    print('data', data)
    channel_id = data.get('channel_id')
    client.chat_postMessage(channel=channel_id, text="Reference #command-log channel for execution progress!")
    user_id = data.get('user_id')
    client.chat_postMessage(channel=user_id, text="recv /get_qrcode")
    return Response(), 200