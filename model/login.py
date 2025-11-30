from datetime import datetime
from helpers import CrudHelper
from schema.login import Login
from schema.user import User
from domain.http_response import HttpResponse
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class LoginModel:

    @staticmethod
    def validate_password_register(password: str):
        if password and len(password) > 128:
            return HttpResponse.bad_request("Password must contain less than 128 characters")
        elif not password:
            return HttpResponse.bad_request("Fill in the password field")
        return True

    @staticmethod
    def insert(
        user: object,
        email: str,
        password: str,
        latest_login: object,
        access_token: str,
        refresh_token: str
    ) -> None:
        if LoginModel.validate_password_register(password):
            login = Login(
                id=str(uuid.uuid4()),
                user=user,
                email=email,
                password=generate_password_hash(password),
                latest_login=latest_login,
                access_token=access_token,
                refresh_token=refresh_token
            )
            if CrudHelper.insert(login):
                CrudHelper.flush_to_database()
                
    @staticmethod
    def update_token_login(
        current_user: object,
        token: str,
        refresh_token: str
    ):
        setattr(current_user, 'access_token', token)
        setattr(current_user, 'refresh_token', refresh_token)
        setattr(current_user, 'logged', True)
        setattr(current_user, 'latest_login', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        LoginModel.commit()
        return User.query \
            .filter(User.id == current_user.user_id) \
            .first_or_404()
        
    @staticmethod
    def get_by_email(
        email: str
    ) -> object:
        return Login.query \
            .filter(Login.email == email) \
            .first_or_404()

    @staticmethod
    def get_by_email_and_password(
        email: str, 
        password: str
    ) -> object:
        login = Login.query \
            .filter(Login.email == email) \
            .first_or_404()
        if check_password_hash(login.password, password):
            return login
        else:
            return None

    @staticmethod
    def get_by_email_and_refresh_token(
        email: str,
        refresh_token: str
    ) -> object:
        return Login.query \
            .filter(
                Login.email == email,
                Login.refresh_token == refresh_token
            ) \
            .first_or_404()

    @staticmethod
    def commit():
        CrudHelper.commit_to_database()

    @staticmethod
    def update(
        current_user: object,
        key: str,
        value
    ) -> None:
        if hasattr(current_user.login[0], key):
            setattr(current_user.login[0], key, generate_password_hash(value))
        else:
            return HttpResponse.bad_request()

    @staticmethod
    def update_code_recovery(
        user: object,
        key: str,
        value
    ) -> None:
        if hasattr(user.login[0], key):
            setattr(user.login[0], key, value)
        else:
            return HttpResponse.bad_request()

    @staticmethod
    def update_code_null(
        login: object,
        key: str,
        value
    ) -> None:
        if hasattr(login, key):
            setattr(login, key, value)
        else:
            return HttpResponse.bad_request()

    @staticmethod
    def rollback_login():
        CrudHelper.rollback_to_database()
