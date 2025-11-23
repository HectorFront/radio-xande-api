from app import app, client_required
from controller import *

@app.route("/api/v1/user/ad", methods=["GET"])
@client_required
def get_ad():
    return AdControl.get_ad()