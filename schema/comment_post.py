from marshmallow import fields
from app import database, serializer

class CommentPost(database.Model):
    __tablename__ = "comment_post"

    id = database.Column(database.String(56), primary_key=True, nullable=False)
    user_id = database.Column(database.String(56), database.ForeignKey('user.id', ondelete="CASCADE"), nullable=True)
    community_post_id = database.Column(database.String(56), database.ForeignKey('community_post.id', ondelete="CASCADE"), nullable=False)
    gif_id = database.Column(database.String(56), database.ForeignKey('gif.id'), nullable=True)
    description = database.Column(database.String(1000), nullable=False)
    date_created = database.Column(database.DateTime, nullable=False)

class CommentPostSchema(serializer.SQLAlchemyAutoSchema):
    date_created = fields.DateTime(format='%Y-%m-%dT%H:%M:%SZ')
    class Meta:
        model = CommentPost
