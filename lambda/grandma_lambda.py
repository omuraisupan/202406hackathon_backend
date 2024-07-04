import json
import boto3
import os

def lambda_handler(event, context):
    print("Received event:", json.dumps(event, indent=2))  # イベント全体をログ

    # AWS Bedrockの設定
    region = 'us-west-2'
    model_id = 'anthropic.claude-3-haiku-20240307-v1:0'
    client = boto3.client('bedrock-runtime', region_name=region)
    
    prompt_text = event.get('prompt', 'こんにちは')
    threads_num = event.get('length', 10)
    level = event.get('level', 1)
    
    # リクエストパラメータの設定
    params = {
        'modelId': model_id,
        'contentType': 'application/json',
        'accept': 'application/json',
        'body': json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 3000,
            'system': f"""
                あなたは2ちゃんねらーです.2Chのスレッドを立ててください.なお，おばあちゃんのような口調でスレッドを立ててください.
                時々ユーモアやジョーク，四字熟語，ことわざを交えつつ，シームレスなレスをください.
                2chでの会話を想定してください.AA等を使っても構いません.
                口の悪さは, 5段階の{level}です.1は言葉遣いが最も丁寧で, 5は罵詈雑言の嵐でデリカシーが皆無です.
                返答は, json形式で返してください. 
                レス数は{threads_num}個にしてください.スレタイはレスには含まれません.
                最初のレスはスレを立てた人です.
                スレタイは2Chにありそうなものにしてください.
                形式は以下の通りです
                [
                {{"title": "スレのタイトル"}},
                    {{
                    "index": "レス番号",
                    "name": "名前",
                    "time": "日付(曜)hh:mm:ss.ms",
                    "id": "ID:ユーザーID",
                    "content": "スレの内容"
                    }},
                    {{
                    "index": "レス番号",
                    "name": "名前",
                    "time": "日付(曜)hh:mm:ss.ms",
                    "id": "ID:ユーザーID",
                    "content": "スレの内容"
                    }},
                    ...
                ]
                名前は, 2chらしい名前や固定ハンドルネームをつけてください.
                同じ人のレスは, 同じIDとコテハンになります.
                時刻はある程度ランダムに設定してください.ただし, 後のレスは前のレスよりも時間が進んでいるようにしてください.
                「はい, わかりました」等の返答は不要です.スレのタイトルから, スレの内容までをJson形式で返してください.
                必要に応じて安価をつけてください
                keyは英語に変換してください 例，名前 -> name
                """,
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': prompt_text
                        }
                    ]
                }
            ]
        })
    }
    
    # モデルの呼び出し
    try:
        response = client.invoke_model(**params)
        response_body = json.loads(response['body'].read().decode('utf-8'))
        response_text = response_body['content'][0]['text']
        print(response_text)
        print(json.dumps({'message': response_text}))
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'message': response_text})
        }
    except KeyError as e:
            print(f"KeyError: {e}")
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': json.dumps({'message': 'Error', 'error': str(e)})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'error': str(e)})
        }
        