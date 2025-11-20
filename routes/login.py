from app import app, jwt_required, client_required
from flask import request
from controller import *
from domain.http_response import HttpResponse

@app.route("/api/v1/user/login", methods=["POST"])
@client_required
def login():
    return LoginControl.login(request)

@app.route('/api/v1/user/oauth/<provider>', methods=['POST'])
@client_required
def oauth_login(provider):
    if provider not in ['google', 'facebook']:
        return HttpResponse.bad_request({'error': 'Provider not supported'})
    return LoginControl.login_oauth(request, provider)

@app.route("/api/v1/user/login/renew_token", methods=["GET"])
@client_required
def renew_token():
    return LoginControl.renew_token(request)

@app.route("/api/v1/user/confirm/code", methods=["POST"])
@client_required
def confirm_code():
    return LoginControl.confirm_code(request)

@app.route("/api/v1/user/change/password", methods=["PATCH"])
@client_required
@jwt_required
def change_password(current_user):
    return LoginControl.update_password(request, current_user)

@app.route("/api/v1/user/logout", methods=["POST"])
@client_required
@jwt_required
def logout(current_user):
    return LoginControl.logout(request, current_user)