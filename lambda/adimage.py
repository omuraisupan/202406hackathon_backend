# import json
# import boto3
# import base64
# import os

# s3_client = boto3.client('s3')
# bedrock_client = boto3.client('bedrock-runtime', region_name='us-west-2')

# def lambda_handler(event, context):
#     model_id = event.get("model_id", "stability.stable-diffusion-xl-v1")
#     text_prompts = event.get("text_prompts", [{"text": "computer with coffee", "weight": 1}])
#     cfg_scale = event.get("cfg_scale", 10)
#     seed = event.get("seed", 0)
#     steps = event.get("steps", 50)
#     width = event.get("width", 512)
#     height = event.get("height", 512)
    
#     params = {
#         "modelId": model_id,
#         "contentType": "application/json",
#         "accept": "application/json",
#         "body": json.dumps({
#             "text_prompts": text_prompts,
#             "cfg_scale": cfg_scale,
#             "seed": seed,
#             "steps": steps,
#             "width": width,
#             "height": height,
#         })
#     }

#     try:
#         response = bedrock_client.invoke_model(**params)
#         response_body = json.loads(response['body'].read())
#         base64_image = response_body['artifacts'][0]['base64']
#         binary_data = base64.b64decode(base64_image)
        
#         output_image_path = "/tmp/output_image.png"
#         with open(output_image_path, "wb") as f:
#             f.write(binary_data)

#         s3_bucket = 'testbucket-202406-hackathon-kaba'
#         s3_key = "output_image.png"
#         s3_client.upload_file(output_image_path, s3_bucket, s3_key)

#         return {
#             'statusCode': 200,
#             'body': json.dumps('Image saved to S3')
#         }
#     except Exception as e:
#         print("Error invoking model:", e)
#         return {
#             'statusCode': 500,
#             'body': json.dumps('Error invoking model')
#         }

import json
import boto3
import base64

bedrock_client = boto3.client('bedrock-runtime', region_name='us-west-2')

def lambda_handler(event, context):
    model_id = event.get("model_id", "stability.stable-diffusion-xl-v1")
    # model_id = event.get("model_id", "amazon.titan-image-generator-v1")
    text_prompts = event.get("text_prompts", [{"text": "Top quality, 1 beautiful woman, Bun Hair, blonde hair, wearing Camisole & skirt, shy-smile, Sunlight, at street", "weight": 1}])
    cfg_scale = event.get("cfg_scale", 10)
    seed = event.get("seed", 0)
    steps = event.get("steps", 50)
    width = event.get("width", 512)
    height = event.get("height", 512)
    styles_preset = event.get("styles_preset", "photographic")
    
    params = {
        "modelId": model_id,
        "contentType": "application/json",
        "accept": "application/json",
        "body": json.dumps({
            "styles_preset": styles_preset,
            "text_prompts": text_prompts,
            "cfg_scale": cfg_scale,
            "seed": seed,
            "steps": steps,
            "width": width,
            "height": height,
        })
    }

    try:
        response = bedrock_client.invoke_model(**params)
        response_body = json.loads(response['body'].read())
        base64_image = response_body['artifacts'][0]['base64']
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({
                'image': base64_image
            }),
            'isBase64Encoded': True
        }
    except Exception as e:
        print("Error invoking model:", e)
        return {
            'statusCode': 500,
            'body': json.dumps('Error invoking model')
        }
