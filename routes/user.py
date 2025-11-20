from app import app, jwt_required, client_required
from flask import request
from controller import *

@app.route("/api/v1/user/register", methods=["POST"])
@client_required
def register():
    return UserControl.user_register(request)

@app.route("/api/v1/user/<id>", methods=["GET", "PUT", "PATCH", "DELETE"])
@jwt_required
@client_required
def user(current_user, id):
    if request.method == "GET":
        return UserControl.user_data(request, current_user)
    elif request.method in ["PUT", "PATCH"]:
        return UserControl.user_update(request, current_user, id)
    elif request.method in ["DELETE"]:
        return UserControl.user_delete(request, current_user, id)