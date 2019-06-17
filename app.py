import os
import re
import sys
import errno
import json
import tempfile
import requests 
from bs4 import BeautifulSoup
from urllib.request import urlretrieve

from flask import Flask, request, abort, send_from_directory

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    MemberJoinedEvent, MemberLeftEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage)

from linebot.exceptions import LineBotApiError

app = Flask(__name__)

channel_access_token ='depzJAsLeVp71tO5p2owx5eqjdNUEBcDfeQ7VsPdYhIIukGZRoCJfxl1wqkSfLEP5lisvgcCiqYXtR6e9hvNVhsfIwJlr11NolM63rfa/mFKUVKYFVnCmWBSIjF8P5FIGwWTqs6abmiHsjGCdvcijQdB04t89/1O/w1cDnyilFU='
channel_secret = 'f966ef65c1fc88deaca1d53cd4a1f963'
if channel_access_token is None:
    sys.exit(1)
if channel_secret is None:
    sys.exit(1)
    
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

def get_exchange_rate_info():
    target_url = 'https://rate.bot.com.tw/xrt?Lang=zh-TW'
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}
    rs = requests.session()
    res = rs.get(target_url,headers=headers)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    currcency = soup.find_all("div",{"class":"hidden-phone print_show"})
    cash_in = soup.find_all("td",{"class":"rate-content-cash text-right print_hide","data-table":"本行現金買入"})
    cash_out = soup.find_all("td",{"class":"rate-content-cash text-right print_hide","data-table":"本行現金賣出"})
    spot_in = soup.find_all("td",{"class":"text-right display_none_print_show print_width","data-table":"本行即期買入"})
    spot_out = soup.find_all("td",{"class":"text-right display_none_print_show print_width","data-table":"本行即期賣出"})
    return {"currcency":currcency,"cash_in":cash_in,"cash_out":cash_out,"spot_in":spot_in,"spot_out":spot_out}
            
# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    print("headers: " + request.headers['X-Line-Signature'])
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'ex_rate':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='ex_rate'))
    else:
        pass

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        cmd =re.split("/",event.message.text)
        if cmd[0] != "":
            message = TextSendMessage(text=event.message.text)
            line_bot_api.reply_message(event.reply_token, message)
        else:
            if cmd[1] == "help":
                content="查詢幣別 : /rate\n查詢匯率 : /rate/幣別ID\n"
                message = TextSendMessage(text=content)
                line_bot_api.reply_message(event.reply_token, message)
            elif cmd[1] == "rate":
                data = get_exchange_rate_info()
                data_index = enumerate([re.split("\r\n",item.text)[1].strip() for index,item in enumerate(data["currcency"])])
                if len(cmd)==2:
                    content = "".join(item + " : " + str(index) + "\n" for index,item in data_index)
                    message = TextSendMessage(text=content)
                    line_bot_api.reply_message(event.reply_token, message)
                elif len(cmd)==3:
                    ind = int(cmd[2])
                    rate = {"currcency":re.split("\r\n",data["currcency"][ind].text)[1].strip(),"cash_in":data["cash_in"][ind].text,"cash_out":data["cash_out"][ind].text,"spot_in":data["spot_in"][ind].text,"spot_out":data["spot_out"][ind].text}
                    content=rate["currcency"] + "\n現金\n" + "買入 : " + rate["cash_in"] + "\n賣出 : " + rate["cash_out"] + "\n即期\n" + "買入 : " + rate["spot_in"] + "\n賣出 : " + rate["spot_out"]
                    message = TextSendMessage(text=content)
                    line_bot_api.reply_message(event.reply_token, message)
                else:
                    pass
                #rate = {"currcency":re.split("\r\n",data["currcency"][currcency_id].text)[1].strip(),"cash_in":data["cash_in"][currcency_id].text,"cash_out":data["cash_out"][currcency_id].text,"spot_in":data["spot_in"][currcency_id].text,"spot_out":data["spot_out"][currcency_id].text}
            else:
                message = TextSendMessage(text="Command not exist.")
                line_bot_api.reply_message(event.reply_token, message)
            """
            image_url = "https://yumetwins.cdn.prismic.io/yumetwins/df97f2deda4e833a45247d07c15b0c136a57937e_465804506659e4c3d02445c894cf5bf8fdadc08a_gu_announcement_01.png"
            img = ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
            line_bot_api.reply_message(event.reply_token,img)
            """
    except LineBotApiError as e:
        raise e

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )
    message = TextSendMessage(text=str(event.message.package_id)+"-"+str(event.message.sticker_id))
    line_bot_api.reply_message(event.reply_token, message)
    
@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
    else:
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '.' + ext
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='Save content.'),
            TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name))
        ])
        
@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix='file-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '-' + event.message.file_name
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='Save file.'),
            TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name))
        ])

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        LocationSendMessage(
            title=event.message.title, address=event.message.address,
            latitude=event.message.latitude, longitude=event.message.longitude
        )
    )
        
@handler.add(JoinEvent)
def handle_join(event):
    newcoming_text = "Hello world."
    line_bot_api.reply_message(event.reply_token,TextMessage(text = newcoming_text))
    print("JoinEvent",JoinEvent)
    
@handler.add(LeaveEvent)
def handle_leave(event):
    print("Leave Event = ", event)
    print("Leave info = ", event.source)

@handler.add(PostbackEvent)
def handle_postback(event):
    pass
    
@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='Got follow event'))

@handler.add(UnfollowEvent)
def handle_unfollow():
    app.logger.info("Got Unfollow event")
    
@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text='Got memberJoined event. event={}'.format(
                event)))

@handler.add(MemberLeftEvent)
def handle_member_left(event):
    app.logger.info("Got memberLeft event")

@app.route("/", methods=['POST'])
def index():
    return "Hello world."

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    #make_static_tmp_dir()
