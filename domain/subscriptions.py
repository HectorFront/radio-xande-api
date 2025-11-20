from infra.environments import env

APP_DOMAIN_RETURN = f'https://{env.get("DOMAIN_WEB")}/#/subscriptions'

PERIOD_STRIPE_PROD = {
    env.get('PRICE_BASIC_PROD'): "month",
    env.get('PRICE_PREMIUM_PROD'): "month",
    env.get('PRICE_BASIC_YEAR_PROD'): "year",
    env.get('PRICE_PREMIUM_YEAR_PROD'): "year"
}

PRODUCTS_STRIPE_PROD = {
    env.get('PRICE_BASIC_PROD'): "basic",
    env.get('PRICE_PREMIUM_PROD'): "premium",
    env.get('PRICE_BASIC_YEAR_PROD'): "basic",
    env.get('PRICE_PREMIUM_YEAR_PROD'): "premium"
}

PERIOD_STRIPE_DEV = {
    env.get('PRICE_BASIC_DEV'): "month",
    env.get('PRICE_PREMIUM_DEV'): "month",
    env.get('PRICE_BASIC_YEAR_DEV'): "year",
    env.get('PRICE_PREMIUM_YEAR_DEV'): "year"
}

PRODUCTS_STRIPE_DEV = {
    env.get('PRICE_BASIC_DEV'): "basic",
    env.get('PRICE_PREMIUM_DEV'): "premium",
    env.get('PRICE_BASIC_YEAR_DEV'): "basic",
    env.get('PRICE_PREMIUM_YEAR_DEV'): "premium"
}