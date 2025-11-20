import time
import threading
from typing import Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import yt_dlp
from infra.environments import env

class YouTubeLiveService:
    def __init__(self):
        self.api_key = env.get('YOUTUBE_API_KEY')
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.live_chat_id = None
        self.next_page_token = None
        self.is_monitoring = False
        
    def get_channel_live_status(self, channel_id: str) -> Dict:
        try:
            request = self.youtube.search().list(
                part='snippet',
                channelId=channel_id,
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
                    return {
                        'is_live': True,
                        'video_id': video_id,
                        'title': video['snippet']['title'],
                        'thumbnail': video['snippet']['thumbnails']['high']['url'],
                        'live_chat_id': self.live_chat_id,
                        'started_at': live_details.get('actualStartTime')
                    }
            
            return {'is_live': False}
        except HttpError as e:
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
    
    def start_chat_monitoring(self, socketio, channel_id: str):
        def monitor():
            self.is_monitoring = True
            while self.is_monitoring:
                try:
                    status = self.get_channel_live_status(channel_id)
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
    
    def stop_chat_monitoring(self):
        self.is_monitoring = False
        self.live_chat_id = None
        self.next_page_token = None