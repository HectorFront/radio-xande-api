from marshmallow import fields
from app import database, serializer

class YouTubeLiveCache(database.Model):
    __tablename__ = "youtube_live_cache"

    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    channel_id = database.Column(database.String(128), nullable=False)
    is_live = database.Column(database.Boolean, nullable=False, default=False)
    video_id = database.Column(database.String(128), nullable=True)
    title = database.Column(database.Text, nullable=True)
    thumbnail = database.Column(database.Text, nullable=True)
    live_chat_id = database.Column(database.String(128), nullable=True)
    started_at = database.Column(database.DateTime, nullable=True)
    cached_at = database.Column(database.DateTime, nullable=False)
    last_live_check = database.Column(database.DateTime, nullable=True)

class YouTubeLiveCacheSchema(serializer.SQLAlchemyAutoSchema):
    started_at = fields.DateTime(format='%Y-%m-%dT%H:%M:%SZ')
    cached_at = fields.DateTime(format='%Y-%m-%dT%H:%M:%SZ')
    last_live_check = fields.DateTime(format='%Y-%m-%dT%H:%M:%SZ')
    
    class Meta:
        model = YouTubeLiveCache