from schema.user import User
from helpers import CrudHelper
from domain.http_response import HttpResponse
import uuid

class UserModel:

    @staticmethod
    def insert(
        name: str,
        email: str,
        date_create_account: object,
        cellphone: str = None,
        income: float = 0,
        picture: str = None,
    ) -> User:
        user = User(
            id=str(uuid.uuid4()),
            name=name,
            balance=0,
            email=email,
            customer=None,
            income=income,
            picture=picture,
            plan='free',
            dark_mode=False,
            subscription=None,
            cellphone=cellphone,
            payment_method=None,
            date_subscription=None,
            date_create_account=date_create_account,
            promotion_expiration=None
        )
        if CrudHelper.insert(user):
            CrudHelper.flush_to_database()
        return user

    @staticmethod
    def get_user(id) -> object:
        return CrudHelper.get_one_by_id(id, User)

    @staticmethod
    def get_by_email(email: str) -> object:
        return User.query.filter(User.email == email).first()
    
    @staticmethod
    def get_by_customer(customer: str) -> object:
        return User.query.filter(User.customer == customer).first()
    
    @staticmethod
    def get_by_payment_method(payment_method: str) -> object:
        return User.query.filter(User.payment_method == payment_method).first()
    
    @staticmethod
    def get_by_subscription(subscription: str) -> object:
        return User.query.filter(User.subscription == subscription).first()

    @staticmethod
    def get_all_users() -> object:
        return User.query.order_by(User.id.asc()).all()

    @staticmethod
    def delete_user(id) -> bool:
        user = CrudHelper.get_one_by_id(id, User)
        if CrudHelper.remove(user):
            UserModel.commit()
            return True
        else:
            return HttpResponse.not_found()

    @staticmethod
    def update(
        current_user: object, 
        key: str, 
        value
    ) -> None:
        if hasattr(current_user, key):
            setattr(current_user, key, value)
        else:
            return HttpResponse.bad_request()

    @staticmethod
    def commit() -> None:
        CrudHelper.commit_to_database()

    @staticmethod
    def rollback_user() -> None:
        CrudHelper.rollback_to_database()
