import os
import boto3
import botocore
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

def download_file_from_s3(file_url) -> bool:
    CURRENT_WORKING_DIR = os.getcwd()
    TARGET_DIR = os.path.join(CURRENT_WORKING_DIR, "uploads")
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        
    parsed_url = urlparse(file_url)
    bucket_name = file_url.split(".s3")[0].split("//")[1]
    object_key = parsed_url.path.lstrip('/')
    s3 = boto3.client('s3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key)
    try:
        target_path = os.path.join(TARGET_DIR,object_key)
        print(target_path)
        s3.download_file("staffagent-dev-resumes", object_key, target_path)
        print(f"File downloaded successfully from {file_url} to {TARGET_DIR}")
        return True
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print(f"The object {object_key} does not exist in bucket {bucket_name}.")
            return False
        else:
            return False