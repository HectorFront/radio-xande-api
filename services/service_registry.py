from services.youtube_live import YouTubeLiveService

class ServiceRegistry:
    _instances = {}
    
    @classmethod
    def get_youtube_service(cls):
        if 'youtube' not in cls._instances:
            cls._instances['youtube'] = YouTubeLiveService()
        return cls._instances['youtube']