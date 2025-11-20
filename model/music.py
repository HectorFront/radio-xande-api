from domain import HttpResponse
from schema.music import Music
from helpers import CrudHelper
from datetime import datetime
import uuid

class MusicModel:
    
    @staticmethod
    def insert(description: str, url_attached: str, image_attached = None, user_id: str = None, duration_ms: int = None) -> Music:
        music = Music(
            id=str(uuid.uuid4()),
            user_id=user_id,
            description=description,
            image_attached=image_attached,
            url_attached=url_attached,
            duration_ms=duration_ms,
            date_created=datetime.now()
        )
        if CrudHelper.insert(music):
            CrudHelper.flush_to_database()
        return music
    
    @staticmethod
    def update(
        music: object, 
        key: str, 
        value
    ) -> None:
        if hasattr(music, key):
            setattr(music, key, value)
        else:
            return HttpResponse.bad_request()

    @staticmethod
    def commit():
        CrudHelper.commit_to_database()

    @staticmethod
    def rollback():
        CrudHelper.rollback_to_database()
    
    @staticmethod
    def get_by_id(music_id: str) -> Music:
        return Music.query.filter_by(id=music_id).first()
    
    @staticmethod
    def get_all():
        return Music.query.all()