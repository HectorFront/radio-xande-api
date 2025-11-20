from app import app, client_required
from flask import request
from gateway import *


@app.route("/api/v1/user/log/errors", methods=["POST"])
@client_required
def log_errors():
    return LogErrorsGateway.register_log(request)
