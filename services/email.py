import smtplib
from random import randint
from services import ServiceLogin
from infra.environments import env
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ServiceEmail:
    
    @staticmethod
    def get_hash_email(email) -> str:
        email = email.split("@")
        email_hash = f"{email[0][0:len(email[0]) // 2]}****@{email[1]}"
        return email_hash
        
    @staticmethod
    def generate_code() -> str:
        code = ''
        for _index in range(6):
            code += str(randint(0, 9))
        return code

    @staticmethod
    def user_set_code(code, request) -> object:
        user = ServiceLogin.login_exists("email", request.json.get("email"))
        ServiceLogin.set_code_recovery(user, "code_recovery", code)
        return user

    @staticmethod
    def template_notification(code: str, username: str) -> str:
        with open("./app/templates/recovery.html", "r", encoding="utf") as email:
            current_notification = email.read()
            new_notification = current_notification.replace("code_recovery", code).replace("username", username)
            return new_notification
    
    @staticmethod
    def send_notification(html: str, receiver: str) -> None:
        email_message = MIMEMultipart()
        email_message['Subject'] = "Mexpenses App"
        email_message['From'] = env.get('EMAIL_SMTP')
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            email_message.set_payload(MIMEText(html, 'html'))
            server.ehlo()
            server.starttls()
            server.login(email_message['From'], env.get('PASSWORD_SMTP'))
            server.sendmail(email_message['From'], receiver, email_message.as_string())