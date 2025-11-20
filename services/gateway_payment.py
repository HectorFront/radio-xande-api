from datetime import datetime
from infra.stripe import stripe
from model.user import UserModel
from domain.http_response import HttpResponse

class ServiceGatewayPayment:
    
    @staticmethod
    def commit_subscription():
        UserModel.commit()
    
    @staticmethod
    def is_trial_over_timestamp(trial_end_date):
        if trial_end_date:
            return datetime.fromtimestamp(trial_end_date) < datetime.now()
        else:
            return False
        
    @staticmethod
    def set_plan(current_user, plan):
        UserModel.update_user(current_user, 'plan', plan)    
        
    @staticmethod
    def set_plan_period(current_user, plan_period):
        UserModel.update_user(current_user, 'plan_period', plan_period)
        
    @staticmethod
    def set_customer(current_user, customer):
        UserModel.update_user(current_user, 'customer', customer)
        
    @staticmethod
    def set_subscription(current_user, subscription):
        UserModel.update_user(current_user, 'subscription', subscription)
    
    @staticmethod
    def set_payment_method(current_user, payment_method):
        UserModel.update_user(current_user, 'payment_method', payment_method)
        
    @staticmethod
    def set_date_subscription(current_user, date):
        UserModel.update_user(current_user, 'date_subscription', date)
    
    @staticmethod
    def set_date_period_end_subscription(current_user, date):
        UserModel.update_user(current_user, 'date_period_end_subscription', date)
        
    @staticmethod
    def set_provider_subscription(current_user, provider_subscription):
        UserModel.update_user(current_user, 'provider_subscription', provider_subscription)

    @staticmethod
    def clear_subscription_current_user(current_user):
        if current_user.customer:
            try:
                stripe.Customer.delete(current_user.customer)
            except Exception:
                pass 
        ServiceGatewayPayment.set_plan(current_user, "free")
        ServiceGatewayPayment.set_plan_period(current_user, None)
        ServiceGatewayPayment.set_customer(current_user, None)
        ServiceGatewayPayment.set_subscription(current_user, None)
        ServiceGatewayPayment.set_payment_method(current_user, None)
        ServiceGatewayPayment.set_date_subscription(current_user, None)
        ServiceGatewayPayment.set_provider_subscription(current_user, None)
        ServiceGatewayPayment.set_date_period_end_subscription(current_user, None)
    
    @staticmethod
    def cancel_subscription(current_user):
        try:
            subscription = None
            if current_user.subscription:
                subscription = stripe.Subscription.retrieve(
                    current_user.subscription
                )
            if subscription and current_user.customer:
                ServiceGatewayPayment.clear_subscription_current_user(current_user)
                ServiceGatewayPayment.commit_subscription()
        except Exception as _err:
            return HttpResponse.unprocessable_entity()
    
    @staticmethod
    def handle_gateway_stripe_payment(current_user):
        subscription = stripe.Subscription.retrieve(current_user.subscription)
        canceled = subscription.status in ('canceled', 'unpaid')
        if canceled:
            timestamp_period_end_subscription = subscription.current_period_end
            datetime_period_end_subscription = datetime.fromtimestamp(timestamp_period_end_subscription)
            ServiceGatewayPayment.set_date_period_end_subscription(current_user, datetime_period_end_subscription)
            if datetime.now().timestamp() > timestamp_period_end_subscription or not timestamp_period_end_subscription:
                ServiceGatewayPayment.clear_subscription_current_user(current_user)
        ServiceGatewayPayment.commit_subscription()
        
    @staticmethod
    def handle_gateway_google_payment(current_user):
        subscription = None
        canceled = False
        pass
        
    @staticmethod
    def handle_gateway_apple_payment(current_user):
        subscription = None
        canceled = False
        pass
    
    @staticmethod
    def handle_user_subscription(current_user):
        if current_user.customer and current_user.subscription:
            Gateways = {
                "stripe": ServiceGatewayPayment.handle_gateway_stripe_payment,
                "google": ServiceGatewayPayment.handle_gateway_google_payment,
                "apple": ServiceGatewayPayment.handle_gateway_apple_payment
            }
            handler = Gateways.get(current_user.provider_subscription)
            if handler:
                handler(current_user)
            else:
                pass