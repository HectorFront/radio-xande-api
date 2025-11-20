from marshmallow import fields
from app import database, serializer

class Gif(database.Model):
    __tablename__ = "gif"

    id = database.Column(database.String(56), primary_key=True, nullable=False)
    user_id = database.Column(database.String(56), database.ForeignKey('user.id', ondelete="CASCADE"), nullable=True)
    url_attached = database.Column(database.Text, nullable=False)
    date_created = database.Column(database.DateTime, nullable=True)

class GifSchema(serializer.SQLAlchemyAutoSchema):
    date_created = fields.DateTime(format='%Y-%m-%dT%H:%M:%SZ')
    class Meta:
        model = Gif
