from flask import jsonify
from helpers import ArrayHelper

class HttpResponse:
    @staticmethod
    def ok(data=None, message="Success"):
        if data:
            return jsonify(data), 200
        elif ArrayHelper.is_array(data):
            return HttpResponse.not_found()
        return jsonify({
            "status": "success",
            "message": message
        }), 200

    @staticmethod
    def created_successfully(data=None, message="Created successfully"):
        if data:
            return jsonify(data), 201
        return jsonify({
            "status": "success",
            "message": message
        }), 201

    @staticmethod
    def bad_request(errors=None, message="Bad request"):
        if errors:
            return jsonify(errors), 400
        return jsonify({
            "status": "fail",
            "message": message
        }), 400

    @staticmethod
    def unauthorized(errors=None, message="Unauthorized"):
        if errors:
            return jsonify(errors), 401
        return jsonify({
            "status": "fail",
            "message": message
        }), 401

    @staticmethod
    def forbidden(errors=None, message="Forbidden"):
        if errors:
            return jsonify(errors), 403
        return jsonify({
            "status": "fail",
            "message": message
        }), 403

    @staticmethod
    def not_found(errors=None, message="Not found"):
        if errors:
            return jsonify(errors), 404
        return jsonify({
            "status": "fail",
            "message": message
        }), 404
        
    @staticmethod
    def conflict(errors=None, message="Conflict"):
        if errors:
            return jsonify(errors), 409
        return jsonify({
            "status": "fail",
            "message": message
        }), 409

    @staticmethod
    def unprocessable_entity(errors=None, message="Unprocessable entity"):
        if errors:
            return jsonify(errors), 422
        return jsonify({
            "status": "fail",
            "message": message
        }), 422

    @staticmethod
    def internal_server_error(errors=None, message="Internal server error"):
        if errors:
            return jsonify(errors), 500
        return jsonify({
            "status": "error",
            "message": message
        }), 500
      
    @staticmethod
    def service_unavailable(errors=None, message="Service Unavailable"):
        if errors:
            return jsonify(errors), 503
        return jsonify({
            "status": "error",
            "message": message
        }), 503
