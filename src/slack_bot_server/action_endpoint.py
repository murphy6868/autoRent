from flask import Blueprint
from flask import request, Response
import slack_sdk as slack
import os
from pathlib import Path
import sys
sys.path.append('src')
import utils

token = utils.getCredentials().slackBotOAuthToken

client = slack.WebClient(token=token)

action_endpoint_bp = Blueprint('action-endpoint', __name__)

@action_endpoint_bp.route('/action-endpoint', methods=['POST'])
def action_endpoint():
  #data = request.get_data()
  #print(data)
  data = request.get_json()
  print(data)
  
  return Response(), 200