import boto3
import tempfile
import os
import re
from PIL import Image
import ffmpeg
from botocore.exceptions import ClientError
from infra.environments import env
from domain.http_response import HttpResponse

class S3UploadException(Exception):
    def __init__(self, message):
        self.response = HttpResponse.bad_request(message=message)

class S3UploadService:
    @staticmethod
    def upload_image(file, filename):
        try:
            bucket_name = env.get('S3_BUCKET_NAME_PUBLIC')
            if not bucket_name:
                raise S3UploadException("S3_BUCKET_NAME_PUBLIC not configured")
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=env.get('S3_ACCESS_KEY'),
                aws_secret_access_key=env.get('S3_SECRET_ACCESS_KEY'),
                endpoint_url=env.get('S3_ENDPOINT_URL_PUBLIC')
            )
            max_image_size = 10 * 1024 * 1024
            
            file.seek(0, 2)
            size = file.tell()
            file.seek(0)
            
            if size > max_image_size:
                raise S3UploadException(f"Image too large. Maximum: {max_image_size / 1024 / 1024}MB")

            with tempfile.NamedTemporaryFile(suffix='.jpg') as temp_file:
                image = Image.open(file)
                
                if image.mode in ('RGBA', 'P'):
                    image = image.convert('RGB')
                
                if image.width > 1920 or image.height > 1080:
                    image.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
                
                image.save(temp_file.name, 'JPEG', quality=85, optimize=True)
                
                return S3UploadService._upload_to_s3(s3_client, bucket_name, temp_file.name, filename, 'image/jpeg')
                
        except Exception as e:
            raise S3UploadException(f"Image upload error: {str(e)}")

    @staticmethod
    def upload_video(file, filename):
        try:
            bucket_name = env.get('S3_BUCKET_NAME_PUBLIC')
            if not bucket_name:
                raise S3UploadException("S3_BUCKET_NAME_PUBLIC not configured")
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=env.get('S3_ACCESS_KEY'),
                aws_secret_access_key=env.get('S3_SECRET_ACCESS_KEY'),
                endpoint_url=env.get('S3_ENDPOINT_URL_PUBLIC')
            )
            max_video_size = 50 * 1024 * 1024
            
            file.seek(0, 2)
            size = file.tell()
            file.seek(0)
            
            if size > max_video_size:
                raise S3UploadException(f"Video too large. Maximum: {max_video_size / 1024 / 1024}MB")

            with tempfile.TemporaryDirectory() as temp_dir:
                input_file = os.path.join(temp_dir, 'input.mp4')
                m3u8_file = os.path.join(temp_dir, 'playlist.m3u8')
                segment_pattern = os.path.join(temp_dir, 'segment_%03d.ts')
                
                with open(input_file, 'wb') as f:
                    f.write(file.read())
                
                (
                    ffmpeg
                    .input(input_file)
                    .output(
                        m3u8_file,
                        format='hls',
                        hls_time=10,
                        hls_list_size=0,
                        hls_segment_filename=segment_pattern,
                        vcodec='libx264',
                        acodec='aac',
                        crf=28,
                        preset='medium',
                        vf='scale=1280:720:force_original_aspect_ratio=decrease'
                    )
                    .overwrite_output()
                    .run(quiet=True)
                )
                
                m3u8_filename = filename.replace('.mp4', '.m3u8')
                S3UploadService._update_m3u8_urls(m3u8_file, m3u8_filename)
                
                s3_client.upload_file(
                    m3u8_file,
                    bucket_name,
                    m3u8_filename,
                    ExtraArgs={'ContentType': 'application/vnd.apple.mpegurl'}
                )
                
                segment_base = filename.replace('.mp4', '_segment')
                for file_name in os.listdir(temp_dir):
                    if file_name.endswith('.ts'):
                        segment_key = f"{segment_base}_{file_name}"
                        segment_path = os.path.join(temp_dir, file_name)
                        s3_client.upload_file(
                            segment_path,
                            bucket_name,
                            segment_key,
                            ExtraArgs={'ContentType': 'video/mp2t'}
                        )
                
                return f"{env.get('S3_REPOSITORY_PUBLIC')}/{m3u8_filename}"
                
        except Exception as e:
            raise S3UploadException(f"Video upload error: {str(e)}")

    @staticmethod
    def upload_audio(file, filename):
        try:
            bucket_name = env.get('S3_BUCKET_NAME_PUBLIC')
            if not bucket_name:
                raise S3UploadException("S3_BUCKET_NAME_PUBLIC not configured")
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=env.get('S3_ACCESS_KEY'),
                aws_secret_access_key=env.get('S3_SECRET_ACCESS_KEY'),
                endpoint_url=env.get('S3_ENDPOINT_URL_PUBLIC')
            )
            max_audio_size = 10 * 1024 * 1024
            
            file.seek(0, 2)
            size = file.tell()
            file.seek(0)
            
            if size > max_audio_size:
                raise S3UploadException(f"Audio too large. Maximum: {max_audio_size / 1024 / 1024}MB")

            with tempfile.TemporaryDirectory() as temp_dir:
                input_file = os.path.join(temp_dir, 'input.mp3')
                m3u8_file = os.path.join(temp_dir, 'playlist.m3u8')
                segment_pattern = os.path.join(temp_dir, 'segment_%03d.ts')
                
                with open(input_file, 'wb') as f:
                    f.write(file.read())
                (
                    ffmpeg
                    .input(input_file)
                    .output(
                        m3u8_file,
                        format='hls',
                        hls_time=10,
                        hls_list_size=0,
                        hls_segment_filename=segment_pattern,
                        acodec='aac',
                        audio_bitrate='128k'
                    )
                    .overwrite_output()
                    .run(quiet=True)
                )
                
                m3u8_filename = filename.replace('.mp3', '.m3u8')
                S3UploadService._update_m3u8_urls(m3u8_file, m3u8_filename)
            
                s3_client.upload_file(
                    m3u8_file,
                    bucket_name,
                    m3u8_filename,
                    ExtraArgs={'ContentType': 'application/vnd.apple.mpegurl'}
                )
                
                segment_base = filename.replace('.mp3', '_segment')
                for file_name in os.listdir(temp_dir):
                    if file_name.endswith('.ts'):
                        segment_key = f"{segment_base}_{file_name}"
                        segment_path = os.path.join(temp_dir, file_name)
                        s3_client.upload_file(
                            segment_path,
                            bucket_name,
                            segment_key,
                            ExtraArgs={'ContentType': 'video/mp2t'}
                        )
                
                return f"{env.get('S3_REPOSITORY_PUBLIC')}/{m3u8_filename}"
                
        except Exception as e:
            raise S3UploadException(f"Audio upload error: {str(e)}")

    @staticmethod
    def delete_file(filename):
        try:
            bucket_name = env.get('S3_BUCKET_NAME_PUBLIC')
            if not bucket_name:
                raise S3UploadException("S3_BUCKET_NAME_PUBLIC not configured")
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=env.get('S3_ACCESS_KEY'),
                aws_secret_access_key=env.get('S3_SECRET_ACCESS_KEY'),
                endpoint_url=env.get('S3_ENDPOINT_URL_PUBLIC')
            )
            
            s3_client.delete_object(Bucket=bucket_name, Key=filename)
            
        except ClientError as e:
            raise S3UploadException(f"S3 delete error: {str(e)}")

    @staticmethod
    def _upload_to_s3(s3_client, bucket_name, file_path, filename, content_type):
        try:
            s3_client.upload_file(
                file_path,
                bucket_name,
                filename,
                ExtraArgs={'ContentType': content_type}
            )
            
            return f"{env.get('S3_REPOSITORY_PUBLIC')}/{filename}"
            
        except ClientError as e:
            raise S3UploadException(f"S3 upload error: {str(e)}")
    
    @staticmethod
    def _update_m3u8_urls(m3u8_file, m3u8_filename):
        try:
            with open(m3u8_file, 'r') as f:
                content = f.read()
            
            segment_base = m3u8_filename.replace('.m3u8', '_segment')
            base_url = env.get('S3_REPOSITORY_PUBLIC')
            
            content = re.sub(
                r'segment_(\d+)\.ts',
                f'{base_url}/{segment_base}_segment_\\1.ts',
                content
            )
            
            with open(m3u8_file, 'w') as f:
                f.write(content)
                
        except Exception as e:
            print(f"Erro ao atualizar URLs do M3U8: {str(e)}")