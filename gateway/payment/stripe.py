from infra.stripe import stripe
from datetime import datetime
from model.user import UserModel
from collections import namedtuple
from services import ServiceGatewayPayment
from domain.http_response import HttpResponse
from domain.subscriptions import APP_DOMAIN_RETURN, PRODUCTS_STRIPE_PROD, PERIOD_STRIPE_PROD

class StripeGateway:

    @staticmethod
    def create_payment(request, _current_user):
        data = namedtuple("Request", request.json.keys())(*request.json.values())
        try:
            intent = stripe.PaymentIntent.create(
                amount=stripe.Price.retrieve(data.product).unit_amount,
                currency="brl",
                automatic_payment_methods={"enabled": True},
            )
            return HttpResponse.ok(intent)
        except Exception as _err:
            return HttpResponse.unprocessable_entity()

    @staticmethod
    def create_payment_method(request, current_user):
        data = namedtuple("Request", request.json.keys())(*request.json.values())
        try:
            payment_method = stripe.PaymentMethod.create(
                type="card",
                card={
                    "number": data.number,
                    "exp_month": data.exp_month,
                    "exp_year": data.exp_year,
                    "cvc": data.cvc,
                },
            )
            existing_payment_method = UserModel.get_by_payment_method(payment_method['id'])
            if existing_payment_method:
                return HttpResponse.conflict()
            ServiceGatewayPayment.set_payment_method(current_user, payment_method['id'])
            ServiceGatewayPayment.commit_subscription()
            return HttpResponse.ok(payment_method)
        except Exception as _err:
            ServiceGatewayPayment.clear_subscription_current_user(current_user)
            ServiceGatewayPayment.commit_subscription()
            return HttpResponse.unprocessable_entity()

    @staticmethod
    def create_customer(request, current_user):
        data = request.json
        try:
            stripe.PaymentMethod.retrieve(current_user.payment_method)
            existing_customers = stripe.Customer.list(email=data.get("email")).data
            if existing_customers:
                customer = existing_customers[0]
            else:
                customer = stripe.Customer.create(
                    name=data.get("name"),
                    email=data.get("email"),
                    payment_method=current_user.payment_method,
                    invoice_settings={"default_payment_method": current_user.payment_method},
                )
            existing_customer = UserModel.get_by_customer(customer['id'])
            if existing_customer:
                return HttpResponse.conflict()
            ServiceGatewayPayment.set_customer(current_user, customer['id'])
            ServiceGatewayPayment.commit_subscription()
            return HttpResponse.ok(customer)
        except Exception as _err:
            ServiceGatewayPayment.clear_subscription_current_user(current_user)
            ServiceGatewayPayment.commit_subscription()
            return HttpResponse.unprocessable_entity()

    @staticmethod
    def create_subscription(request, current_user):
        data = request.json    
        try:
            stripe.PaymentMethod.retrieve(current_user.payment_method)
            stripe.Customer.retrieve(current_user.customer)
            plan_period = PERIOD_STRIPE_PROD.get(data.get("product"))
            plan_product = PRODUCTS_STRIPE_PROD.get(data.get("product"))
            if plan_product == data.get("plan"):
                subscription = stripe.Subscription.create(
                    customer=current_user.customer,
                    items=[
                        {"price": data.get("product")},
                    ],
                    trial_period_days=0
                )
                existing_subscription = UserModel.get_by_subscription(subscription['id'])
                if existing_subscription:
                    return HttpResponse.conflict()
                ServiceGatewayPayment.set_plan(current_user, plan_product)
                ServiceGatewayPayment.set_plan_period(current_user, plan_period)
                ServiceGatewayPayment.set_provider_subscription(current_user, 'stripe')
                ServiceGatewayPayment.set_subscription(current_user, subscription['id'])
                ServiceGatewayPayment.set_date_subscription(current_user, datetime.now())
                ServiceGatewayPayment.commit_subscription()
                return HttpResponse.ok(subscription)
            else:
                ServiceGatewayPayment.clear_subscription_current_user(current_user)
                ServiceGatewayPayment.commit_subscription()
                return HttpResponse.bad_request("Plan product is not available")
        except Exception as _err:
            ServiceGatewayPayment.clear_subscription_current_user(current_user)
            ServiceGatewayPayment.commit_subscription()
            return HttpResponse.unprocessable_entity()
           
    @staticmethod
    def retrieve_subscription(_request, current_user):
        try:
            subscription = {}
            if current_user.subscription:
                subscription = stripe.Subscription.retrieve(
                    current_user.subscription
                )
            return HttpResponse.ok(subscription)
        except Exception as _err:
            return HttpResponse.unprocessable_entity()
            
    @staticmethod 
    def payments_method_data(_request, current_user):
        try:
            payments_method_data = {}
            if current_user.customer:
                payments_method_data = stripe.PaymentMethod.list(
                    customer=current_user.customer,
                    type="card",
                )
            return HttpResponse.ok(payments_method_data)
        except Exception as _err:
            return HttpResponse.unprocessable_entity()

    @staticmethod    
    def attach_payment_method(request, current_user):
        data = request.json
        try:
            attach = stripe.PaymentMethod.attach(
                data.get("payment_method"),
                customer=current_user.customer,
            )
            ServiceGatewayPayment.set_payment_method(data.get("payment_method"))
            ServiceGatewayPayment.commit_subscription()
            return HttpResponse.ok(attach)
        except Exception as _err:
            return HttpResponse.unprocessable_entity()

    @staticmethod
    def customer_portal(_request, current_user):
        try:
            portal_session = None
            if current_user.customer:
                portal_session = stripe.billing_portal.Session.create(
                    customer=current_user.customer,
                    return_url=APP_DOMAIN_RETURN,
                )
            if not portal_session:
                return HttpResponse.not_found("Portal customer not found")
            return HttpResponse.ok(portal_session)
        except Exception as _err:
            return HttpResponse.unprocessable_entity()


    