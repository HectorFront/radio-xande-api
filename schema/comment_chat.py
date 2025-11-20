from marshmallow import fields
from app import database, serializer

class CommentChat(database.Model):
    __tablename__ = "comment_chat"

    id = database.Column(database.String(56), primary_key=True, nullable=False)
    user_id = database.Column(database.String(56), database.ForeignKey('user.id', ondelete="CASCADE"), nullable=True)
    gif_id = database.Column(database.String(56), database.ForeignKey('gif.id'), nullable=True)
    description = database.Column(database.String(1000), nullable=False)
    url_attached = database.Column(database.Text, nullable=True)
    date_created = database.Column(database.DateTime, nullable=False)

class CommentChatSchema(serializer.SQLAlchemyAutoSchema):
    date_created = fields.DateTime(format='%Y-%m-%dT%H:%M:%SZ')
    class Meta:
        model = CommentChat
