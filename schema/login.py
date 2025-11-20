from marshmallow import fields
from app import database, serializer

class Login(database.Model):
    __tablename__ = "login"

    id = database.Column(database.String(56), primary_key=True, nullable=False)
    user_id = database.Column(database.String(56), database.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    email = database.Column(database.String(128), nullable=False, unique=True)
    password = database.Column(database.String(256), nullable=False)
    latest_login = database.Column(database.DateTime, nullable=False)
    logged = database.Column(database.Boolean, nullable=True)
    access_token = database.Column(database.String(256), nullable=True, unique=True)
    refresh_token = database.Column(database.String(256), nullable=True, unique=True)
    code_recovery = database.Column(database.String(6), nullable=True)
    timing_recovery = database.Column(database.DateTime, nullable=True)

class LoginSchema(serializer.SQLAlchemyAutoSchema):
    timing_recovery = fields.DateTime(format='%Y-%m-%dT%H:%M:%SZ')
    latest_login = fields.DateTime(format='%Y-%m-%dT%H:%M:%SZ')
    class Meta:
        model = Login
