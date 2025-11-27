from marshmallow import fields
from app import database, serializer

class VoteUpPost(database.Model):
    __tablename__ = "vote_up_post"

    id = database.Column(database.String(56), primary_key=True, nullable=False)
    user_id = database.Column(database.String(56), database.ForeignKey('user.id', ondelete="CASCADE"), nullable=True)
    community_post_id = database.Column(database.String(56), database.ForeignKey('community_post.id', ondelete="CASCADE"), nullable=True)
    date_created = database.Column(database.DateTime, nullable=False)

class VoteUpPostSchema(serializer.SQLAlchemyAutoSchema):
    date_created = fields.DateTime(format='%Y-%m-%dT%H:%M:%SZ')
    class Meta:
        model = VoteUpPost
