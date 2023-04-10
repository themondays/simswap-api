import os
import boto3
import json
from config import load_config

config = load_config()

AWS_ACCESS_KEY = config['aws']['access_key']
AWS_SECRET_ACCESS_KEY = config['aws']['secret_access_key']
AWS_PROFILE = config['aws']['profile_name']

s3 = boto3.client('s3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

s3 = boto3.client('s3',)

session = boto3.Session(profile_name=AWS_PROFILE)
client = session.client('s3')

def upload(bucket, src, dst):
    try:
        client.upload_file(src, bucket, dst)
        return True
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        return False

def download(bucket, src, dst):
    try:
        client.download_file(bucket, src, dst)
        with open(dst) as task_file:
            return json.load(task_file)
    except Exception as e:
        print(f"Error downloading file from S3: {e}")
        return None
