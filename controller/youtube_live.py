from domain.http_response import HttpResponse
from services.youtube_live import YouTubeLiveService
from domain.youtube import YT_CHANNEL_ID_SUPERXANDAO
from model.youtube_live_cache import YouTubeLiveCacheModel

class YouTubeLiveControl:
    
    @staticmethod
    def get_live_status():
        try:
            youtube_service = YouTubeLiveService()
            status = youtube_service.get_channel_live_status()
            if 'error' in status:
                return HttpResponse.service_unavailable(status)
            return HttpResponse.ok(status)
        except Exception as e:
            return HttpResponse.internal_server_error({'error': str(e)})
    
    @staticmethod
    def get_chat_messages(request):
        try:
            page_token = request.args.get('pageToken')
            cache_youtube_live = YouTubeLiveCacheModel.get_cache(YT_CHANNEL_ID_SUPERXANDAO)
            live_chat_id = cache_youtube_live.live_chat_id if cache_youtube_live else None
            
            youtube_service = YouTubeLiveService()
            youtube_service.live_chat_id = live_chat_id
            messages = youtube_service.get_live_chat_messages(page_token)
            
            if 'error' in messages:
                return HttpResponse.service_unavailable(messages)
            return HttpResponse.ok(messages)
        except Exception as e:
            return HttpResponse.internal_server_error({'error': str(e)})