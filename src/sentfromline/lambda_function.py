import requests
import os
import json
import boto3
from io import BytesIO
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info("saveImageFromLine...........")

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
BUCKET_NAME = os.environ["BUCKET_NAME"]

#-- Headerの生成
HEADER = {
    'Content-type':
    'application/json',
    'Authorization':
    'Bearer ' + LINE_CHANNEL_ACCESS_TOKEN,
}

s3 = boto3.resource('s3')
def lambda_handler(event, context):
    body = json.loads(event['body'])
    for event in body['events']:
        #-- LINEからimage（画像)が届いた時
        if event['message']['type'] == 'image':
            #-- 1. 画像を読み出し
            MessageId = event['message']['id']  # メッセージID
            ImageFile = requests.get('https://api-data.line.me/v2/bot/message/'+ MessageId +'/content',headers=HEADER) #Imagecontent取得
            Image_bin = BytesIO(ImageFile.content)
            Image = Image_bin.getvalue()  # 画像取得

            #--2. xxxx.jpgに保存
            filename=MessageId+'.jpg'
            obj = s3.Object(BUCKET_NAME,filename)
            obj.put( Body=Image )
            print('file %s saved at %s!' %(filename,BUCKET_NAME))
            msg='画像が保存されました!'
        else:
            msg='画像が送信されていません!'

        #-- LINEに返す情報
        REQUEST_MESSAGE = [
            {
            'type': 'text',
            'text': msg,
            }
        ]
        payload = {'replyToken': event['replyToken'], 'messages': REQUEST_MESSAGE}

        #-- HEADERとmessages(payload)を付加してpost
        if len(payload['messages']) > 0:
            response = requests.post(
                'https://api.line.me/v2/bot/message/reply',
                headers=HEADER,
                data=json.dumps(payload)
            )
    return 0