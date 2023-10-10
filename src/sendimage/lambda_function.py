import json
import os
import logging
import boto3
 
 
logger = logging.getLogger()
logger.setLevel(logging.INFO)
 
CONNECTION_TABLE = os.environ['CONNECTION_TABLE']
IMAGE_S3_BUCKET_NAME = os.environ['IMAGE_S3_BUCKET_NAME']
WEBSOCKET_ENDPOINT_URL = os.environ['WEBSOCKET_ENDPOINT_URL']

S3_ENDPOINT_URL = f'https://{IMAGE_S3_BUCKET_NAME}.s3.ap-northeast-1.amazonaws.com'
 
def lambda_handler(event, context):
 
    dynamodb = boto3.resource('dynamodb')
    connection_table = dynamodb.Table(CONNECTION_TABLE)
 
    try:
        # DynamoDBに存在するコネクションIDを全て取得
        items = connection_table.scan(ProjectionExpression='connection_id').get('Items')
    except Exception as e:
        logger.error("error1")
        logger.error(e)
 
    selected_image = event['Records'][0]['s3']['object']['key']
    logger.info(selected_image)
    apigw_management = boto3.client('apigatewaymanagementapi', endpoint_url=WEBSOCKET_ENDPOINT_URL)
    for item in items:
        try:
            # 画像保存先のS3 URLを構成して、コネクションごとにデータとしてそのURLを送る
            image_s3 = f'{S3_ENDPOINT_URL}/{selected_image}'
            apigw_management.post_to_connection(ConnectionId=item['connection_id'], Data=image_s3)
            logger.info(f'ConnectionID: {item["connection_id"]}, image: {image_s3}')
        except Exception as e:
            logger.error("error2")
            logger.error(e)
            return {'statusCode': 500, 'body': e.message}
    
    return {'statusCode': 200, 'body': 'Data sent.'}