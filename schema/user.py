from marshmallow import fields
from app import database, serializer
from schema.login import LoginSchema

class User(database.Model):
    __tablename__ = "user"

    id = database.Column(database.String(56), primary_key=True, nullable=False)
    name = database.Column(database.String(256), nullable=False)
    email = database.Column(database.String(128), nullable=False, unique=True)
    admin = database.Column(database.Boolean, nullable=True)
    moderator = database.Column(database.Boolean, nullable=True)
    banned = database.Column(database.Boolean, nullable=True)
    banned_until_date = database.Column(database.DateTime, nullable=True)
    plan = database.Column(database.Text, nullable=True)
    customer = database.Column(database.Text, nullable=True)
    subscription = database.Column(database.Text, nullable=True)
    payment_method = database.Column(database.Text, nullable=True)
    plan_period = database.Column(database.String(32), nullable=True)
    date_subscription = database.Column(database.DateTime, nullable=True)
    date_period_end_subscription = database.Column(database.DateTime, nullable=True)
    provider_subscription = database.Column(database.String(6), nullable=True)
    date_created = database.Column(database.DateTime, nullable=False)
    picture = database.Column(database.Text, nullable=True)

    login = database.relationship('Login', backref="user", cascade="all, delete")

class UserSchema(serializer.SQLAlchemyAutoSchema):
    date_subscription = fields.DateTime(format='%Y-%m-%dT%H:%M:%SZ')
    date_period_end_subscription = fields.DateTime(format='%Y-%m-%dT%H:%M:%SZ')
    date_created = fields.DateTime(format='%Y-%m-%dT%H:%M:%SZ')
    login = serializer.Nested(LoginSchema, many=True, exclude=["password", "code_recovery", "timing_recovery", "user_id", "logged",  "email", "id"])
    class Meta:
        model = User

class DataUserSchema(serializer.SQLAlchemyAutoSchema):
    date_subscription = fields.DateTime(format='%Y-%m-%dT%H:%M:%SZ')
    date_period_end_subscription = fields.DateTime(format='%Y-%m-%dT%H:%M:%SZ')
    date_created = fields.DateTime(format='%Y-%m-%dT%H:%M:%SZ')
    class Meta:
        model = User