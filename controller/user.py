import requests
from datetime import datetime
from helpers import FieldsHelper
from model.user import UserModel
from model.login import LoginModel
from domain.http_response import HttpResponse
from schema.user import DataUserSchema, UserSchema
from services import ServiceLogin, ServiceGatewayPayment, ServiceUsername

class UserControl:

    @staticmethod
    def user_data(_request, current_user):
        ServiceGatewayPayment.handle_user_subscription(current_user)
        return HttpResponse.ok(DataUserSchema(many=False).dump(current_user))
    
    @staticmethod
    def user_delete(_request, current_user, id):
        if current_user.id == id:
            ServiceGatewayPayment.cancel_subscription(current_user)
            if UserModel.delete_user(current_user.id):
                return HttpResponse.ok()
        else:
            return HttpResponse.forbidden()

    @staticmethod
    def user_update(request, current_user, id):
        if current_user.id == id:
            data = request.json
            user = UserModel.get_by_id(current_user.id)
            update = {
                "name": data.get('name', user.name),
                "email": data.get('email', user.email)
            }
            for key, value in update.items():
                if FieldsHelper.is_valid_field(value):
                    UserModel.update_user(current_user, key, value)
            UserModel.commit()
            return HttpResponse.ok()
        else:
            return HttpResponse.forbidden()
        
    @staticmethod
    def oauth_register(request, provider: str):
        data = request.json
        access_token = data.get('access_token')
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
        if db_user:
            return HttpResponse.conflict()
        picture_url = None
        if provider == 'facebook':
            picture_data = user_info.get('picture')
            if picture_data and isinstance(picture_data, dict):
                picture_url = picture_data.get('data', {}).get('url')
        elif provider == 'google':
            picture_url = user_info.get('picture')
        try:
            username = ServiceUsername.create_username(user_info.get("name"))
            user = UserModel.insert(
                user_info.get("name"), 
                user_info.get("email"),
                username,
                datetime.now(),
                picture_url
            )
            LoginModel.insert(
                user,
                user.email,
                access_token,
                datetime.now(),
                ServiceLogin.create_token(user),
                ServiceLogin.create_refresh_token(user)
            )
            UserModel.commit()
            LoginModel.commit()
            return HttpResponse.ok(UserSchema(many=False).dump(user))
        except Exception as err:
            return HttpResponse.bad_request(err)

    @staticmethod
    def user_register(request):
        data = request.json
        try:
            username = ServiceUsername.create_username(data.get("name"))
            user = UserModel.insert(
                data.get("name"), 
                data.get("email"),
                username,
                datetime.now(),
                data.get("picture", None)
            )
            LoginModel.insert(
                user,
                data.get("password"),
                datetime.now(),
                ServiceLogin.create_token(user),
                ServiceLogin.create_refresh_token(user)
            )
            UserModel.commit()
            LoginModel.commit()
            return HttpResponse.ok(UserSchema(many=False).dump(user))
        except AttributeError as err:
            return HttpResponse.bad_request(err)