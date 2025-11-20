import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError
from werkzeug.exceptions import HTTPException
import datetime
import requests
from flask import current_app
from model.login import Login
from model.login import LoginModel
from model.user import UserModel
from schema.user import UserSchema
from services import ServiceLogin
from domain.http_response import HttpResponse

class LoginControl:

    @staticmethod
    def login(request):
        data = request.json
        current_user = LoginModel.get_by_email_and_password(
            data.get("email"),
            data.get("password")
        )
        if current_user:
            new_token = ServiceLogin.create_token(current_user)
            new_refresh_token = ServiceLogin.create_refresh_token(current_user)
            user = LoginModel.update_token_login(current_user, new_token, new_refresh_token)
            LoginModel.commit()
            return HttpResponse.ok(UserSchema(many=True).dump(user))
        return HttpResponse.not_found()

    @staticmethod
    def login_oauth(request, provider: str):
        access_token = request.json.get('access_token')
        if not access_token:
            return HttpResponse.bad_request({'error': 'Access token required'})
        if provider == 'google':
            user_info_response = requests.get(
                'https://www.googleapis.com/oauth2/v3/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )
        elif provider == 'facebook':
            user_info_response = requests.get(
                'https://graph.facebook.com/me',
                params={
                    'fields': 'id,name,email,picture',
                    'access_token': access_token
                }
            )
        else:
            return HttpResponse.bad_request({'error': 'Unsupported provider'})
        if user_info_response.status_code != 200:
            return HttpResponse.unauthorized()
        user_info = user_info_response.json()
        email = user_info.get('email')
        if not email:
            return HttpResponse.bad_request({'error': f'Email unavailable {provider.title()}'})
        db_user = UserModel.get_by_email(email)
        if not db_user:
            return HttpResponse.not_found()
        current_user = LoginModel.get_by_email(db_user.email)
        new_token = ServiceLogin.create_token(current_user)
        new_refresh_token = ServiceLogin.create_refresh_token(current_user)
        user = LoginModel.update_token_login(current_user, new_token, new_refresh_token)
        LoginModel.commit()
        return HttpResponse.ok(UserSchema(many=True).dump(user))

    @staticmethod
    def renew_token(request):
        refresh_token = request.headers.get('Authorization')
        try:
            decoded = jwt.decode(refresh_token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = LoginModel.get_by_email_and_refresh_token(decoded.get("email"), refresh_token)
            if current_user:
                if ServiceLogin.platform_is_mobile(request):
                    new_token_app = ServiceLogin.create_token_app(current_user)
                    new_refresh_token_app = ServiceLogin.create_refresh_token(current_user)
                    LoginModel.update_token_login_app(current_user, new_token_app, new_refresh_token_app)
                    LoginModel.commit()
                    return HttpResponse.ok({
                        "access_token_app": new_token_app,
                        "refresh_token_app": new_refresh_token_app
                    })
                else:
                    new_token = ServiceLogin.create_token(current_user)
                    new_refresh_token = ServiceLogin.create_refresh_token(current_user)
                    LoginModel.update_token_login(current_user, new_token, new_refresh_token)
                    LoginModel.commit()
                    return HttpResponse.ok({
                        "access_token": new_token,
                        "refresh_token": new_refresh_token
                    })
        except (DecodeError, ExpiredSignatureError, HTTPException):
            return HttpResponse.unauthorized()

    @staticmethod
    def confirm_code(request):
        login = ServiceLogin.get_login("email", request.json.get("email")).login[0]
        if login.code_recovery == request.json.get("code_recovery") and datetime.datetime.now() <= login.timing_recovery:
            ServiceLogin.set_code_null(login)
            Login.query.filter_by(email=login.email).update(
                dict(
                    access_token=ServiceLogin.create_token(login),
                    access_token_app=ServiceLogin.create_token_app(login)
                )
            )
            LoginModel.commit()
            return HttpResponse.ok({
                "access_token": login.access_token,
                "access_token_app": login.access_token_app
            })
        else:
            return HttpResponse.unauthorized()

    @staticmethod
    def update_password(request, current_user):
        data = request.json
        if len(data.get("password")) > 128:
            return HttpResponse.bad_request("Password must contain less than 128 characters")
        else:
            LoginModel.update(current_user, "password", data.get("password"))
            LoginModel.commit()
            return HttpResponse.ok()
    
    @staticmethod
    def logout(request, current_user):
        if current_user.login[0].logged:
            login = Login.query.filter(Login.user_id == current_user.id)
            if ServiceLogin.platform_is_mobile(request):
                login.update(dict(access_token_app=None, logged_app=False))
            else:
                login.update(dict(access_token=None, logged=False))
            LoginModel.commit()
            return HttpResponse.ok()