from app import app, client_required
from domain.http_response import HttpResponse

@app.route("/api/v1/user/healthcheck", methods=["GET"])
@client_required
def health_check():
    return HttpResponse.ok({ "status": "online" })