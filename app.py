from line_bot_api import *
from events.basic import *
from oil import *
from events.Msg_Template import *
from model.mongodb import *
import re #有爬蟲
import twstock #股價
import datetime
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
    profile =line_bot_api.get_profile(event.source.user_id)
    uid=profile.user_id #偵測使用者id
    message_text = str(event.message.text).lower()
    msg=str(event.message.text).upper().strip() #請使用者輸入內容
    emsg=event.message.text
    user_name =profile.display_name #使用者名稱
########################使用說明##################### 
    if message_text =='@使用說明':
        about_us_event(event)
        Usage(event)
########################油價查詢#####################
    if event.message.text == "想知道油價":
        content = oil_price()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content)) 
#########################股票區stack######################### 
    if event.message.text == "股價查詢":
        line_bot_api.push_message(uid,TextSendMessage("請輸入#加股票代號...."))
#股價查詢
    if re.match("想知道股價[0-9]:", msg):
        msg=msg[5:]
        btn_msg = stock_reply_other(msg)
        line_bot_api.push_message(uid, btn_msg)
        return 0
    

#新增使用者關注的股票mongodb
    if re.match('關注[0-9]{4}[<>][0-9]',msg):
        stockNumber=msg[2:6]
        line_bot_api.push_message(uid, TextSendMessage("加入股票代號"+stockNumber))
        content=write_my_stock(uid ,user_name ,stockNumber,msg[6:7],msg[7:])
        line_bot_api.push_message(uid, TextSendMessage(content))
        return 0
    

    if (msg.startswith('#')):
        text = msg[1:]
        content =''

        stock_rt = twstock.realtime.get(text)
        my_datetime = datetime.datetime.fromtimestamp(stock_rt['timestamp']+8*60*60)
        my_time = my_datetime.strftime('%H:%M:%S')

        content +='%s (%s) %s\n' % (
            stock_rt['info']['name'],
            stock_rt['info']['code'],
            my_time)
        
        content += '現價: %s / 開盤: %s\n'%(
            stock_rt['realtime']['latest_trade_price'],
            stock_rt['realtime']['open'])
        content += '最高: %s / 最低:%s\n'%(
            stock_rt['realtime']['high'],
            stock_rt['realtime']['low'])
        
        content += '量: %s\n'%(stock_rt['realtime']['accumulate_trade_volume'])

        stock = twstock.Stock(text)
        content += '-----\n'
        content += '最近五日價格: \n'
        price5 = stock.price[-5:][::-1]
        date5 = stock.date[-5:][::-1]
        for i in range(len(price5)):
            content += '[%s] %s\n' % (date5[i].strftime("%Y-%m-%d"), price5[i])
        line_bot_api.reply_message(
            event.reply_token, 
            TextSendMessage(text=content)
        )
################################匯率區###################################################
    if re.match('幣別種類',emsg):
        message = show_Button()
        line_bot_api.reply_message(event.reply_token,message)

@handler.add(FollowEvent)
def handle_follow(event):
    welcome_msg ="""Hello! 您好，感謝您解除封鎖!
    請別再封鎖我了QQ
    -這裡有股票&匯率資訊~
    -直接點選下方💛圖中💛選單功能
    -Welcome you!"""
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=welcome_msg))  

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    print(event)

if __name__ == "__main__":
    app.run()