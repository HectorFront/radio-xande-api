from app import app, jwt_required, client_required
from flask import request
from gateway import StripeGateway

@app.route("/api/v1/user/subscription/retrieve", methods=["GET"])
@jwt_required
@client_required
def stripe_retrieve_subscription(current_user):
    return StripeGateway.retrieve_subscription(request, current_user)

@app.route("/api/v1/user/payment_method/create", methods=["POST"])
@jwt_required
@client_required
def stripe_payment_method_create(current_user):
    return StripeGateway.create_payment_method(request, current_user)

@app.route("/api/v1/user/customer/portal", methods=["GET"])
@jwt_required
@client_required
def stripe_customer_portal(current_user):
    return StripeGateway.customer_portal(request, current_user)

@app.route("/api/v1/user/subscription/create", methods=["POST"])
@jwt_required
@client_required
def stripe_create_subscription(current_user):
    return StripeGateway.create_subscription(request, current_user)

@app.route("/api/v1/user/customer/create", methods=["POST"])
@jwt_required
@client_required
def stripe_create_customer(current_user):
    return StripeGateway.create_customer(request, current_user)

@app.route("/api/v1/user/payment/create", methods=["POST"])
@jwt_required
@client_required
def stripe_create_payment(current_user):
    return StripeGateway.create_payment(request, current_user)