from marshmallow import fields
from app import database, serializer

class VoteBadPost(database.Model):
    __tablename__ = "vote_bad_post"

    id = database.Column(database.String(56), primary_key=True, nullable=False)
    user_id = database.Column(database.String(56), database.ForeignKey('user.id', ondelete="CASCADE"), nullable=True)
    community_post_id = database.Column(database.String(56), database.ForeignKey('community_post.id', ondelete="CASCADE"), nullable=True)
    date_created = database.Column(database.DateTime, nullable=False)

class VoteBadPostSchema(serializer.SQLAlchemyAutoSchema):
    date_created = fields.DateTime(format='%Y-%m-%dT%H:%M:%SZ')
    class Meta:
        model = VoteBadPost