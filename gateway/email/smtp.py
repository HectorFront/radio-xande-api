from model.user import UserModel
from schema.user import UserSchema
from domain.http_response import HttpResponse
from helpers import ArrayHelper
from services import ServiceEmail

class EmailGateway:
    
    templates_html_available = [""]

    @staticmethod
    def recovery_password(request) -> dict:
        code = ServiceEmail.generate_code()
        user = ServiceEmail.user_set_code(code, request)
        html_with_username = ServiceEmail.template_notification(code, user.name.split(" ")[0])
        ServiceEmail.send_notification(html_with_username, user.email)
        email_hash = ServiceEmail.get_hash_email(user.email)
        return HttpResponse.ok({"email": email_hash})

    @staticmethod
    def send_email_custom(request):
        data = request.json
        if data.get("template") in EmailGateway.templates_html_available:
            filter_send = data.get("filter")
            if filter_send == 'platform':
                users = UserSchema(many=True).dump(UserModel.get_all_users())
                for user in users:
                    html = open(f"./app/templates/{data.get('template')}.html", "r", encoding="utf").read()
                    html_with_username = html.replace("username", user["name"].split(" ")[0])
                    try:
                        ServiceEmail.send_notification(html_with_username, user["email"])
                    except Exception:
                        pass
                return HttpResponse.ok()
            elif ArrayHelper.is_array(filter_send):
                for email in filter_send:
                    html = open(f"./app/templates/{data.get('template')}.html", "r", encoding="utf").read()
                    try:
                        ServiceEmail.send_notification(html, email)
                    except Exception:
                        pass
                return HttpResponse.ok()
            else:
                HttpResponse.bad_request()
        else:
            HttpResponse.forbidden()