import os
import sys
import errno
import json
import tempfile

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

channel_access_token = os.getenv('depzJAsLeVp71tO5p2owx5eqjdNUEBcDfeQ7VsPdYhIIukGZRoCJfxl1wqkSfLEP5lisvgcCiqYXtR6e9hvNVhsfIwJlr11NolM63rfa/mFKUVKYFVnCmWBSIjF8P5FIGwWTqs6abmiHsjGCdvcijQdB04t89/1O/w1cDnyilFU=',None)
channel_secret = os.getenv('f966ef65c1fc88deaca1d53cd4a1f963',None)
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
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        message = TextSendMessage(text=event.message.text)
        line_bot_api.reply_message(event.reply_token, message)
        """
        image_url = "https://yumetwins.cdn.prismic.io/yumetwins/df97f2deda4e833a45247d07c15b0c136a57937e_465804506659e4c3d02445c894cf5bf8fdadc08a_gu_announcement_01.png"
        img = ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
        line_bot_api.reply_message(event.reply_token,img)
        """
    except LineBotApiError as e:
        raise e



@app.route("/", methods=['POST'])
def index():
    return "Hello world."

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    make_static_tmp_dir()
