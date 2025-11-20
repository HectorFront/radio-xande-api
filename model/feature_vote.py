from schema.feature_vote import FeatureVote
from helpers import CrudHelper
from domain.http_response import HttpResponse

class FeatureVoteModel:

    @staticmethod
    def insert(
        email: str,
        feature: str,
        date_created: object
    ) -> None:
        feature_vote = FeatureVote(
            email=email,
            feature=feature,
            date_created=date_created
        )
        CrudHelper.insert(feature_vote)

    @staticmethod
    def commit() -> None:
        CrudHelper.commit_to_database()

    @staticmethod
    def remove(feature: object) -> None:
        if CrudHelper.remove(feature):
            FeatureVoteModel.commit()
            return True
        else:
            return HttpResponse.not_found()
    
    @staticmethod
    def update(
        feature_vote: object,
        key: str,
        value
    ) -> None:
        if hasattr(feature_vote, key):
            setattr(feature_vote, key, value)
        else:
            return HttpResponse.bad_request()

    @staticmethod
    def get_feature_vote_by_id(feature_vote_id: int) -> object:
        return FeatureVote.query \
            .filter(FeatureVote.id == feature_vote_id) \
            .first_or_404()

    @staticmethod
    def get_feature_vote_by_email(email: str) -> object:
        return FeatureVote.query \
            .filter(FeatureVote.email == email) \
            .first_or_404()
