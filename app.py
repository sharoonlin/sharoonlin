from line_bot_api import *
from events.basic import *
from oil import *
app=Flask(__name__)
#處理訊息
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

# 處理訊息callback the same message 
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message_text = str(event.message.text).lower()
    #####################使用說明 選單 油價查詢

    if message_text =='@使用說明':
        about_us_event(event)
        Usage(event)

    if event.message.text == "想知道油價":
        content = oil_price()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content)) 
@handler.add(FollowEvent)
def handle_follow(event):
    welcome_msg ="""Hello! 您好，歡迎您成為HiHi的好友!
    我是提醒小天使
    -這裡有股票&匯率資訊~
    -直接點選下方[圖中]選單功能
    -Welcome you!"""
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=welcome_msg))  

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    print(event)

if __name__ == "__main__":
    app.run()