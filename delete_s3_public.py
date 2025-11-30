import boto3
from dotenv import load_dotenv
import os

load_dotenv()

s3 = boto3.client(
    "s3",
    endpoint_url="https://hel1.your-objectstorage.com",
    aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY"),
)

bucket = os.getenv("S3_BUCKET_NAME_PUBLIC")
response = s3.list_objects_v2(Bucket=bucket)

while response.get("Contents"):
    objects = [{"Key": obj["Key"]} for obj in response["Contents"]]
    s3.delete_objects(Bucket=bucket, Delete={"Objects": objects})
    print(f"Deletados {len(objects)} objetos")
    response = s3.list_objects_v2(Bucket=bucket)

print("Bucket limpo!")
