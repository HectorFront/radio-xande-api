from marshmallow import fields
from app import database, serializer

class FeatureVote(database.Model):
    __tablename__ = "feature_vote"

    id = database.Column(database.Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = database.Column(database.String(56), database.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    feature = database.Column(database.String(256), nullable=False)
    date_created = database.Column(database.DateTime, nullable=False)

class FeatureVoteSchema(serializer.SQLAlchemyAutoSchema):
    date_created = fields.DateTime(format='%Y-%m-%dT%H:%M:%SZ')

    class Meta:
        model = FeatureVote