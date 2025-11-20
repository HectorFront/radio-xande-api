from datetime import datetime
from model.user import UserModel
from model.login import LoginModel
from schema.user import DataUserSchema
from domain.http_response import HttpResponse
from helpers import FieldsHelper
from services import ServiceLogin, ServiceGatewayPayment

class UserControl:

    @staticmethod
    def user_data(_request, current_user):
        ServiceGatewayPayment.handle_user_subscription(current_user)
        return HttpResponse.ok(DataUserSchema(many=True).dump(current_user))
    
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
            user = UserModel.get_user(current_user.id)
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
    def user_register(request):
        data = request.json
        try:
            user = UserModel.insert(
                data.get("name"), 
                data.get("email"), 
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
            return HttpResponse.ok()
        except AttributeError as err:
            return HttpResponse.bad_request(err)