from schema import *
from flask import abort, make_response, jsonify
from app import database
from sqlalchemy.exc import IntegrityError, OperationalError
from typing import Any

class CrudHelper:

    @staticmethod
    def insert(object: object) -> bool:
        database.session.add(object)
        return True

    @staticmethod
    def remove(object: object) -> bool:
        database.session.delete(object)
        return True

    @staticmethod
    def update(key: property, value: Any, new_value: Any, schema: object) -> None:
        if hasattr(schema, key):
            _key = getattr(schema, key).name
            _table = getattr(schema, "__table__")
            try:
                query = _table.update().where(_table.c[key] == value).values({key: new_value})
                database.session.execute(query)
                database.session.commit()
            except Exception as err:
                abort(404, err.args)

    @staticmethod
    def get_one_by_object_key(key: str, value: Any, schema: object) -> object:
        if hasattr(schema, key):
            _key = getattr(schema, key).name
            _table = getattr(schema, "__table__")
            return schema.query.filter(_table.c[key] == value).first()

    @staticmethod
    def get_one_by_id(id: int, schema: object) -> object:
        return schema.query.filter(schema.id == id).first()

    @staticmethod
    def get_all_by_object_key(key: str, value: Any, schema: object) -> object:
        return schema.query.filter(key == value).all()

    @staticmethod
    def commit_to_database() -> None:
        try: 
            database.session.commit() 
        except (AssertionError, IntegrityError, OperationalError) as err:
            CrudHelper.rollback_to_database()
            field = err.orig.args[1].replace(".", " ").replace("'", "")
            if "Duplicate entry" in field:
                response = make_response(jsonify(message=field, conflict=field.split()[-1]), 409)
                return abort(response)
            else:
                response = make_response(jsonify(message="Bad Request, invalid field."), 400)
                return abort(response)
    
    @staticmethod
    def rollback_to_database() -> None:
        database.session.rollback()

    @staticmethod
    def flush_to_database() -> None:
        try: 
            database.session.flush() 
        except (AssertionError, IntegrityError) as err:
            CrudHelper.rollback_to_database()
            field = err.orig.args[1].replace(".", " ").replace("'", "")
            if "Duplicate entry" in field:
                response = make_response(jsonify(message=field, conflict=field.split()[-1]), 409)
                return abort(response)
            else:
                response = make_response(jsonify(message="Bad Request"), 400)
                return abort(response)