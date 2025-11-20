import stripe
from infra.environments import env

stripe.api_key = env.get('STRIPE_API_KEY_PROD')