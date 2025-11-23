    
import re
import json
import time
import yt_dlp
import requests
import threading
from datetime import datetime
from typing import Dict, Optional
from infra.environments import env
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from domain.youtube import YT_CHANNEL_ID_SUPERXANDAO
from schema.youtube_live_cache import YouTubeLiveCache
from model.youtube_live_cache import YouTubeLiveCacheModel

class YouTubeLiveService:
    
    def __init__(self):
        self.api_key = env.get('YOUTUBE_API_KEY')
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.live_chat_id = None
        self.next_page_token = None
        self.is_monitoring = False
        
    def reset_youtube_live_cache(self):
        YouTubeLiveCacheModel.upsert_cache(
            channel_id=YT_CHANNEL_ID_SUPERXANDAO,
            is_live=False,
            video_id=None,
            title=None,
            thumbnail=None,
            live_chat_id=None,
            started_at=None
        )
        
    def get_channel_live_status(self) -> Dict:
        cached_data = YouTubeLiveCacheModel.get_cache(YT_CHANNEL_ID_SUPERXANDAO)
        if cached_data:
            self.live_chat_id = cached_data.live_chat_id
            if not cached_data.is_live and not self._should_check_live(cached_data.last_live_check):
                self.reset_youtube_live_cache()
                return {'is_live': False}
            # Update live check
            if self._should_check_live(cached_data.last_live_check):
                is_live_check = self._check_live_by_crawler()
                if not is_live_check:
                    self.reset_youtube_live_cache()
                    YouTubeLiveCacheModel.update_live_check(YT_CHANNEL_ID_SUPERXANDAO)
                    return {'is_live': False}
            # Return data from cache
            if cached_data.is_live:
                return {
                    'is_live': cached_data.is_live,
                    'video_id': cached_data.video_id,
                    'title': cached_data.title,
                    'thumbnail': cached_data.thumbnail,
                    'live_chat_id': cached_data.live_chat_id,
                    'started_at': cached_data.started_at.strftime('%Y-%m-%dT%H:%M:%S') if cached_data.started_at else None
                }
        # Not cache or need to check live status
        try:
            request = self.youtube.search().list(
                part='snippet',
                channelId=YT_CHANNEL_ID_SUPERXANDAO,
                eventType='live',
                type='video',
                maxResults=1
            )
            response = request.execute()
            if response['items']:
                video = response['items'][0]
                video_id = video['id']['videoId']
                video_request = self.youtube.videos().list(
                    part='liveStreamingDetails',
                    id=video_id
                )
                video_response = video_request.execute()
                if video_response['items']:
                    live_details = video_response['items'][0].get('liveStreamingDetails', {})
                    self.live_chat_id = live_details.get('activeLiveChatId')
                    started_at = live_details.get('actualStartTime')
                    started_at_dt = None
                    if started_at:
                        try:
                            started_at_dt = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                        except:
                            started_at_dt = None
                    YouTubeLiveCacheModel.upsert_cache(
                        channel_id=YT_CHANNEL_ID_SUPERXANDAO,
                        is_live=True,
                        video_id=video_id,
                        title=video['snippet']['title'],
                        thumbnail=video['snippet']['thumbnails']['high']['url'],
                        live_chat_id=self.live_chat_id,
                        started_at=started_at_dt
                    )
                    return {
                        'is_live': True,
                        'video_id': video_id,
                        'title': video['snippet']['title'],
                        'thumbnail': video['snippet']['thumbnails']['high']['url'],
                        'live_chat_id': self.live_chat_id,
                        'started_at': started_at_dt.strftime('%Y-%m-%dT%H:%M:%S') if started_at_dt else None
                    }
            YouTubeLiveCacheModel.upsert_cache(
                channel_id=YT_CHANNEL_ID_SUPERXANDAO,
                is_live=False
            )
            return {'is_live': False}
        except HttpError as e:
            fallback_cache = YouTubeLiveCache.query.filter(
                YouTubeLiveCache.channel_id == YT_CHANNEL_ID_SUPERXANDAO
            ).order_by(YouTubeLiveCache.cached_at.desc()).first()
            
            if fallback_cache:
                self.live_chat_id = fallback_cache.live_chat_id
                return {
                    'is_live': fallback_cache.is_live,
                    'video_id': fallback_cache.video_id,
                    'title': fallback_cache.title,
                    'thumbnail': fallback_cache.thumbnail,
                    'live_chat_id': fallback_cache.live_chat_id,
                    'started_at': fallback_cache.started_at.strftime('%Y-%m-%dT%H:%M:%S') if fallback_cache.started_at else None,
                    'cached': True
                }
            return {'error': f'YouTube API error: {e}', 'is_live': False}
    
    def get_stream_url(self, video_id: str) -> Optional[str]:
        try:
            ydl_opts = {
                'format': 'best[ext=m4a]/best',
                'quiet': True,
                'no_warnings': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
                for format_info in info.get('formats', []):
                    if format_info.get('protocol') == 'm3u8_native':
                        return format_info.get('url')
                return info.get('url')
        except Exception as e:
            print(f"Erro ao obter stream URL: {e}")
            return None
    
    def get_live_chat_messages(self, page_token: str = None) -> Dict:
        if not self.live_chat_id:
            return {'messages': [], 'nextPageToken': None}
        try:
            request = self.youtube.liveChatMessages().list(
                liveChatId=self.live_chat_id,
                part='snippet,authorDetails',
                pageToken=page_token,
                maxResults=200
            )
            response = request.execute()
            messages = []
            for item in response.get('items', []):
                snippet = item['snippet']
                author = item['authorDetails']
                messages.append({
                    'id': item['id'],
                    'message': snippet['displayMessage'],
                    'author': {
                        'name': author['displayName'],
                        'channel_id': author['channelId'],
                        'profile_image': author['profileImageUrl'],
                        'is_moderator': author.get('isChatModerator', False),
                        'is_owner': author.get('isChatOwner', False)
                    },
                    'timestamp': snippet['publishedAt'],
                    'type': snippet['type']
                })
            return {
                'messages': messages,
                'nextPageToken': response.get('nextPageToken'),
                'pollingIntervalMillis': response.get('pollingIntervalMillis', 5000)
            }    
        except HttpError as e:
            return {'error': f'Chat API error: {e}', 'messages': []}
    
    def start_chat_monitoring(self, socketio):
        def monitor():
            self.is_monitoring = True
            while self.is_monitoring:
                try:
                    status = self.get_channel_live_status(YT_CHANNEL_ID_SUPERXANDAO)
                    socketio.emit('live_status', status)
                    if status.get('is_live') and self.live_chat_id:
                        chat_data = self.get_live_chat_messages(self.next_page_token)
                        if chat_data['messages']:
                            socketio.emit('live_chat', chat_data['messages'])
                        self.next_page_token = chat_data.get('nextPageToken')
                        interval = chat_data.get('pollingIntervalMillis', 5000) / 1000
                        time.sleep(interval)
                    else:
                        time.sleep(30)
                        
                except Exception as e:
                    print(f"Erro no monitoramento: {e}")
                    time.sleep(10)
        
        thread = threading.Thread(target=monitor)
        thread.daemon = True
        thread.start()
    
    def _should_check_live(self, last_check: datetime) -> bool:
        if not last_check:
            return True
        return (datetime.now() - last_check).total_seconds() > 15

    def _check_live_by_crawler(self):
        url = f"https://www.youtube.com/channel/{YT_CHANNEL_ID_SUPERXANDAO}/live"
        html = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0"
        }).text
        return '"isLive":true' in html
    
    def stop_chat_monitoring(self):
        self.is_monitoring = False
        self.live_chat_id = None
        self.next_page_token = None