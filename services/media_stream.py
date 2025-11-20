import requests
import re
from infra import env
from mutagen import File
from flask import Response, abort

class MediaStreamService:
    
    @staticmethod
    def get_duration_ms(file_obj):
        try:
            media_file = File(file_obj)
            if media_file and media_file.info.length:
                return int(media_file.info.length * 1000)
            return None
        except:
            return None
    
    @staticmethod
    def stream_media(filename):
        file_url = f"{env.get('S3_REPOSITORY_PUBLIC')}/{filename}"
        try:
            response = requests.get(file_url)
            if response.status_code != 200:
                abort(404)
        except:
            abort(404)
        if filename.endswith('.m3u8'):
            content = response.text
            content = re.sub(
                r'https://[^/]+/[^/]+/[^/]+/([^/]+\.ts)',
                r'\1',
                content
            )
            return Response(
                content,
                headers={
                    'Content-Type': 'application/vnd.apple.mpegurl',
                    'Cache-Control': 'no-cache'
                }
            )
        elif filename.endswith('.ts'):
            return Response(
                response.content,
                headers={
                    'Content-Type': 'video/mp2t',
                    'Content-Length': response.headers.get('Content-Length')
                }
            )
        return Response(
            response.content,
            headers={
                'Content-Type': response.headers.get('Content-Type', 'application/octet-stream'),
                'Content-Length': response.headers.get('Content-Length')
            }
        )