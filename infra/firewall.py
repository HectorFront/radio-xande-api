from flask import Response

class FirewallRequestMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request_method = environ['REQUEST_METHOD']
        allowed_methods = ['GET','HEAD','POST','PUT','PATCH','DELETE','OPTIONS']
        if request_method not in allowed_methods:
            response = Response(status=444)
            return response(environ, start_response)
        return self.app(environ, start_response)