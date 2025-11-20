import jwt
import datetime
from app import app
from helpers import CrudHelper
from schema.user import User
from model.login import LoginModel

class ServiceLogin:
    
    @staticmethod
    def create_token(user):
        payload = {'email': user.email, 'exp': datetime.datetime.now() + datetime.timedelta(hours=48)}
        token = jwt.encode(
            payload, app.config['SECRET_KEY'], algorithm="HS256")
        return token

    @staticmethod
    def create_refresh_token(user):
        payload = {'email': user.email, 'exp': datetime.datetime.now() + datetime.timedelta(days=365)}
        token = jwt.encode(
            payload, app.config['SECRET_KEY'], algorithm="HS256")
        return token
    
    @staticmethod
    def login_exists(key, value):
        if login := ServiceLogin.get_login(key, value):
            return login
        return False

    @staticmethod
    def get_login(key, value):
        return CrudHelper.get_one_by_object_key(key, value, User)
    
    @staticmethod
    def set_code_recovery(login, key, value):
        LoginModel.update_code_recovery(login, key, value)
        LoginModel.update_code_recovery(login, "timing_recovery", datetime.datetime.now() + datetime.timedelta(minutes=20))
        LoginModel.commit()
    
    @staticmethod
    def set_code_null(login):
        LoginModel.update_code_null(login, "code_recovery", None)
        LoginModel.update_code_null(login, "timing_recovery", None)
        LoginModel.commit()