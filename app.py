from line_bot_api import *
from events.basic import *
from oil import *
from events.Msg_Template import *
from events.EXRate import *
from model.mongodb import *
import re #有爬蟲
import twstock #股價
import datetime
app=Flask(__name__)
#抓使用者設定它關心的股票

def cache_users_stock():
    db= constructor_stock()
    nameList =db.list_collection_names()
    users=[]
    for i in range(len(nameList)):
        collect =db[nameList[i]]
        cel = list(collect.find({"tag":'stock'}))
        users.append(cel)
    return users

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
 #查詢股票篩選條件清單 
    if re.match ('股票清單',msg):
        line_bot_api.push_message(uid,TextSendMessage('稍等一下，股票查詢中...'))
        content=show_stock_setting(user_name,uid)
        line_bot_api.push_message(uid,TextSendMessage(content))
        return 0   
#刪除存在資料庫裏面的股票
    if re.match('刪除[0-9]{4}',msg):
        content = delete_my_stock(user_name,msg[2:])
        line_bot_api.push_message(uid,TextSendMessage(content))
        return 0
#清空存在資料庫裡面的股票
    if re.match('清空股票',msg):
        content = delete_my_all_stock(user_name,msg[2:])
        line_bot_api.push_message(uid,TextSendMessage(content))
        return 0 

#清空存在資料庫裡面的股票
    

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
        
    if re.match("換匯[A-Z]{3}/[A-Z{3}]",msg):
        msg=msg[4:]
        content=showCurency(msg) # show 前面的currency
        line_bot_api.push_message(uid,TextSendMessage("將為您做外匯計算...."))
        content = getExchangeRate(msg)
        line_bot_api.push_message(uid, TextSendMessage(content))

    if re.match("股價提醒", msg):
            import schedule
            import time
            # 查看當前股價
            def look_stock_price(stock, condition, price, userID):
                print(userID)
                url = 'https://tw.stock.yahoo.com/q/q?s=' + stock
                list_req = requests.get(url)
                soup = BeautifulSoup(list_req.content, "html.parser")
                getstock= soup.findAll('b')[1].text
                content = stock + "當前股市價格為: " +  getstock
                if condition == '<':
                    content += "\n篩選條件為: < "+ price
                    if float(getstock) < float(price):
                        content += "\n符合" + getstock + " < " + price + "的篩選條件"
                        line_bot_api.push_message(userID, TextSendMessage(text=content))
                elif condition == '>':
                    content += "\n篩選條件為: > "+ price
                    if float(getstock) > float(price):
                        content += "\n符合" + getstock + " > " + price + "的篩選條件"
                        line_bot_api.push_message(userID, TextSendMessage(text=content))
                elif condition == "=":
                    content += "\n篩選條件為: = "+ price
                    if float(getstock) == float(price):
                        content += "\n符合" + getstock + " = " + price + "的篩選條件"
                        line_bot_api.push_message(userID, TextSendMessage(text=content))
            def job():
                print('HH')
                line_bot_api.push_message(uid, TextSendMessage("快買股票喔!"))
                dataList = cache_users_stock()
                # print(dataList)
                for i in range(len(dataList)):
                    for k in range(len(dataList[i])):
                        # print(dataList[i][k])
                        look_stock_price(dataList[i][k]['favorite_stock'], dataList[i][k]['condition'], dataList[i][k]['price'], dataList[i][k]['userID'])
            schedule.every(30).seconds.do(job).tag('daily-tasks-stock'+uid,'second') #每10秒執行一次
            #schedule.every().hour.do(job) #每小時執行一次
            #schedule.every().day.at("17:19").do(job) #每天9點30執行一次
            #schedule.every().monday.do(job) #每週一執行一次
            #schedule.every().wednesday.at("14:45").do(job) #每週三14點45執行一次
            # 無窮迴圈
            while True: 
                schedule.run_pending()
                time.sleep(1)

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