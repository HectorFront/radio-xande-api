import jwt
from functools import wraps
from schema.user import User
from schema.login import Login
from infra.environments import env
from flask import current_app, request
from werkzeug.exceptions import HTTPException
from domain.http_response import HttpResponse
from jwt.exceptions import DecodeError, ExpiredSignatureError

def jwt_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return HttpResponse.unauthorized("Invalid or expired token")
        try:
            decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter(User.email == decoded.get("email")).join(Login, Login.email == User.email) \
                .filter(
                    (Login.access_token == token) | (Login.refresh_token == token)
                ).first_or_404()

        except (DecodeError, ExpiredSignatureError, HTTPException):
            return HttpResponse.unauthorized("Invalid or expired token")
        return function(current_user=current_user, *args, **kwargs)
    return wrapper

def client_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        header_key_platform = request.headers.get('key-platform')
        if header_key_platform == env.get('KEY_PLATFORM_WEB') or header_key_platform == env.get('KEY_PLATFORM_MOBILE'):
            return function(*args, **kwargs)
        else:
            return HttpResponse.forbidden()
    return wrapper