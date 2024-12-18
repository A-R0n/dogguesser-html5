import boto3


def read_file_from_s3(file_name):
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket='dogguesser', Key=file_name)
    data = obj['Body'].read()
    return data