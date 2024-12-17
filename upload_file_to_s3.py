import time
import boto3
# from werkzeug.utils import secure_filename
from boto3.s3.transfer import TransferConfig
import _io
import io


def get_time() -> str:
    return str(time.time_ns())

def get_file_ext(file: _io.BufferedReader) -> str:
    return str(file.name).split(".")[1]

def set_new_file_name(curr_time: str, file_ext: str) -> str:
    return curr_time + "." + file_ext

def set_config() -> TransferConfig:
    return TransferConfig(multipart_threshold=1024*250, max_concurrency=10, multipart_chunksize=1024*250, use_threads=True)

def upload_file_to_s3(file: _io.BufferedReader) -> str:
    curr_time = get_time()
    new_file_name = set_new_file_name(curr_time, 'jpg')
    # we shouldnt need to santize the filname because we define acceptable file types before upload
    # filename = secure_filename(file.filename)
    config = set_config()
    s3 = boto3.client('s3')
    try:
        print(f'attemtpting upload...')
        # import time
        # time.sleep(5)
        s3.upload_fileobj(
            io.BytesIO(file),
            'dogguesser',
            new_file_name,
            ExtraArgs={
                "ACL": "public-read",
                "ContentType": f'image/.jpg'
            },
            Config=config
        )
    except Exception as e:
        print(f'file not uploaded: {e}')
