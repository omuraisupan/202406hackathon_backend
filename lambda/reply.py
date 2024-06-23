import json
import boto3
import os

def lambda_handler(event, context):
    print("Received event:", json.dumps(event, indent=2))  # イベント全体をログ

    # AWS Bedrockの設定
    region = 'us-west-2'
    model_id = 'anthropic.claude-3-haiku-20240307-v1:0'
    #model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    client = boto3.client('bedrock-runtime', region_name=region)


    pre_thread = event.get('pre_thread', [])
    reply_text = event.get('reply', 'こんにちは')
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
                あなたは掲示板の住民です。返信に対して、続きのレスを返してください。
                以前のスレの内容は、次のJsonです。{pre_thread}
                以前のスレイ内容は以下の形式です。
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

                口の悪さは, 5段階の{level}です. 1が最も丁寧で, 5がこの世の終わりレベルで口の悪い設定です.
                返答は, json形式で返してください. 
                続きのレス数は{threads_num}個にしてください.スレタイはレスには含まれません.
                indexは元のレスの番を2つ飛ばして引き継いでください.
                timeは元のレスの時間を引き継いでください.
                同じ人のレスは, 同じIDとコテハンになります.
                形式は以下の通りです. 必ず以下の形式に従ってください.
                [
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
                それぞれのレスはウィットに富んだものにしてください.
                keyは英語に変換してください 例，名前 -> name
                """,
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': reply_text
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
