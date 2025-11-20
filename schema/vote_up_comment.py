from marshmallow import fields
from app import database, serializer

class VoteUpComment(database.Model):
    __tablename__ = "vote_up_comment"

    id = database.Column(database.String(56), primary_key=True, nullable=False)
    user_id = database.Column(database.String(56), database.ForeignKey('user.id', ondelete="CASCADE"), nullable=True)
    comment_chat_id = database.Column(database.String(56), database.ForeignKey('comment_chat.id', ondelete="CASCADE"), nullable=True)
    date_created = database.Column(database.DateTime, nullable=False)

class VoteUpCommentSchema(serializer.SQLAlchemyAutoSchema):
    date_created = fields.DateTime(format='%Y-%m-%dT%H:%M:%SZ')
    class Meta:
        model = VoteUpComment