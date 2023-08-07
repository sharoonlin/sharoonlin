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

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)


if __name__ == "__main__":
    app.run()