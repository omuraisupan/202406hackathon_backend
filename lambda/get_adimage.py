import base64
import boto3
import json

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # リクエストから画像のキーを取得
    object_key = event['image']
    
    try:
        # S3から画像を取得
        response = s3.get_object(
            Bucket='testbucket-202406-hackathon-kaba',
            Key=object_key,
        )
        
        # バイナリデータとして画像を読み込む
        image = response['Body'].read()
        
        # Base64エンコードしてレスポンスとして返す
        encoded_image = base64.b64encode(image).decode('utf-8')
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'image/png'
            },
            'body': encoded_image,
            'isBase64Encoded': True
        }
    
    except Exception as e:
        # エラーが発生した場合の処理
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error_message': str(e)
            })
        }

