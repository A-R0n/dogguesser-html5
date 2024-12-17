import time
import boto3
# from werkzeug.utils import secure_filename
from boto3.s3.transfer import TransferConfig


def get_time() -> str:
    return str(time.time_ns())

def get_file_ext(file) -> str:
    return str(file.filename).split(".")[1]

def set_new_file_name(curr_time: str, file_ext: str) -> str:
    return curr_time + "." + file_ext

def set_config() -> TransferConfig:
    return TransferConfig(multipart_threshold=1024*250, max_concurrency=10, multipart_chunksize=1024*250, use_threads=True)

def upload_file_to_s3(file) -> str:
    curr_time = get_time()
    file_ext = get_file_ext(file)
    new_file_name = set_new_file_name(curr_time, file_ext)
    # we shouldnt need to santize the filname because we define acceptable file types before upload
    # filename = secure_filename(file.filename)
    config = set_config()
    s3 = boto3.client('s3')
    try:
        print(f'attemtpting upload...')
        with open(file.filename, 'rb') as img:
            s3.upload_fileobj(
                img,
                'dogguesser',
                new_file_name,
                ExtraArgs={
                    "ACL": "public-read",
                    "ContentType": file.content_type
                },
                Config=config
            )
    except Exception as e:
        print(f'file not uploaded: {e}')
