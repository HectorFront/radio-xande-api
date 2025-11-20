from app import app, client_required
from flask import request
from controller import *
from gateway import *

@app.route("/api/v1/user/send/email/platform", methods=["POST"])
@client_required
def send_email_custom():
    return EmailGateway.send_email_custom(request)

@app.route("/api/v1/user/recovery/password", methods=["POST"])
@client_required
def recovery_password():
    return EmailGateway.recovery_password(request)