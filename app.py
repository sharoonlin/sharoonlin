#載入linebot 所需的軟件
from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler, exceptions)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *        #* means all

app=Flask(__name__)
# paste your "Channel Access Token"
line_bot_api = LineBotApi('BWD6SYM1M59YQ8n21+p2s28YE3p9O1IQwSC7FReV4BXPvmkJracng3ypR83+rfjb8a8xxQJWan2k/hjliIlcu+3ka5NASprXh+C2efgKnnTb7XJnmqiATsz6t10sR0Te4pmxnAZ49xApEtKeqWz7vQdB04t89/1O/w1cDnyilFU=')
#paste your "Channel Secret" 
handler= WebhookHandler('8e632b1c1583f4817a80f3312d027e1b')

@app.route("/callback",methods=['POST'])
def callback():
    signature =request.headers=['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body,signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'