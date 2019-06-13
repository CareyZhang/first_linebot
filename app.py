import json

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

from linebot.exceptions import LineBotApiError

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('depzJAsLeVp71tO5p2owx5eqjdNUEBcDfeQ7VsPdYhIIukGZRoCJfxl1wqkSfLEP5lisvgcCiqYXtR6e9hvNVhsfIwJlr11NolM63rfa/mFKUVKYFVnCmWBSIjF8P5FIGwWTqs6abmiHsjGCdvcijQdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('f966ef65c1fc88deaca1d53cd4a1f963')

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
    try:
        """
        message = TextSendMessage(text=event.message.text)
        quick_reply = {
				"type": "text",
				"text": "Select your favorite food category or send me your location!",
				"quickReply": {
					"items": [
						{
							"type": "action",
							"action": {
										"type": "message",
										"label": "Sushi",
										"text": "Sushi"
							}
						},
						{
							"type": "action",
							"action": {
										"type": "message",
										"label": "Tempura",
										"text": "Tempura"
							}
						},
						{
							"type": "action",
							"action": {
										"type": "location",
										"label": "Send location"
							}
						}
					]
				}
			}
        line_bot_api.reply_message(event.reply_token, message)
        #line_bot_api.reply_message(event.reply_token, quick_reply)
        """
        image_url = "https://yumetwins.cdn.prismic.io/yumetwins/df97f2deda4e833a45247d07c15b0c136a57937e_465804506659e4c3d02445c894cf5bf8fdadc08a_gu_announcement_01.png"
        img = ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
        line_bot_api.reply_message(to,img)
    except LineBotApiError as e:
        message = TextSendMessage(text=type(event.message.text))
        line_bot_api.reply_message(event.reply_token, message)
        raise e

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
