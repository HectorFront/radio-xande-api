from marshmallow import fields
from app import database, serializer

class CommunityPost(database.Model):
    __tablename__ = "community_post"

    id = database.Column(database.String(56), primary_key=True, nullable=False)
    user_id = database.Column(database.String(56), database.ForeignKey('user.id', ondelete="CASCADE"), nullable=True)
    is_meme = database.Column(database.Boolean, nullable=True)
    is_notice = database.Column(database.Boolean, nullable=True)
    is_generic = database.Column(database.Boolean, nullable=True)
    is_blocked_comments = database.Column(database.Boolean, nullable=True)
    description = database.Column(database.String(1000), nullable=False)
    video_attached = database.Column(database.Text, nullable=True)
    image_attached = database.Column(database.Text, nullable=True)
    gif_attached = database.Column(database.String(56), database.ForeignKey('gif.id'), nullable=True)
    date_created = database.Column(database.DateTime, nullable=False)

class CommunityPostSchema(serializer.SQLAlchemyAutoSchema):
    date_created = fields.DateTime(format='%Y-%m-%dT%H:%M:%SZ')
    class Meta:
        model = CommunityPost