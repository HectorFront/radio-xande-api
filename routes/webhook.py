from app import app
from flask import request
from gateway import StripeGateway

@app.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    return StripeGateway.stripe_webhook(request)