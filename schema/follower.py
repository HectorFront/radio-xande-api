from marshmallow import fields
from app import database, serializer

class Follower(database.Model):
    __tablename__ = "follower"

    id = database.Column(database.String(56), primary_key=True, nullable=False)
    user_id_profile = database.Column(database.String(56), database.ForeignKey('user.id', ondelete="CASCADE"), nullable=True)
    user_id_follower = database.Column(database.String(56), database.ForeignKey('user.id', ondelete="CASCADE"), nullable=True)
    date_created = database.Column(database.DateTime, nullable=False)

class FollowerSchema(serializer.SQLAlchemyAutoSchema):
    date_created = fields.DateTime(format='%Y-%m-%dT%H:%M:%SZ')
    class Meta:
        model = Follower
