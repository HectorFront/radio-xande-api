from schema.youtube_live_cache import YouTubeLiveCache
from helpers import CrudHelper
from datetime import datetime, date
from typing import Optional

class YouTubeLiveCacheModel:

    @staticmethod
    def get_cache(channel_id: str) -> Optional[YouTubeLiveCache]:
        return YouTubeLiveCache.query.filter(
            YouTubeLiveCache.channel_id == channel_id
        ).first()
        
    @staticmethod
    def delete_cache(channel_id: str) -> bool:
        cache = YouTubeLiveCacheModel.query.filter(
            YouTubeLiveCache.channel_id == channel_id
        ).first()
        if CrudHelper.remove(cache):
            YouTubeLiveCacheModel.commit()
            return True

    @staticmethod
    def upsert_cache(
        channel_id: str,
        is_live: bool,
        video_id: str = None,
        title: str = None,
        thumbnail: str = None,
        live_chat_id: str = None,
        started_at: datetime = None
    ) -> YouTubeLiveCache:
        now = datetime.now()
        cache = YouTubeLiveCache.query.filter(
            YouTubeLiveCache.channel_id == channel_id
        ).first()
        if cache:
            cache.is_live = is_live
            cache.video_id = video_id
            cache.title = title
            cache.thumbnail = thumbnail
            cache.live_chat_id = live_chat_id
            cache.started_at = started_at
            cache.cached_at = now
        else:
            cache = YouTubeLiveCache(
                channel_id=channel_id,
                is_live=is_live,
                video_id=video_id,
                title=title,
                thumbnail=thumbnail,
                live_chat_id=live_chat_id,
                started_at=started_at,
                cached_at=now
            )
            CrudHelper.insert(cache)
        CrudHelper.flush_to_database()
        YouTubeLiveCacheModel.commit()
        return cache

    @staticmethod
    def update_live_check(channel_id: str) -> None:
        cache = YouTubeLiveCache.query.filter(
            YouTubeLiveCache.channel_id == channel_id
        ).first()
        if cache:
            cache.last_live_check = datetime.now()
            CrudHelper.flush_to_database()
            CrudHelper.commit_to_database()

    @staticmethod
    def commit():
        CrudHelper.commit_to_database()