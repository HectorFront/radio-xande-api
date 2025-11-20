from flask import render_template

class ServiceFeatureVote:
    
    @staticmethod
    def template_success():
        return render_template("feature_vote_success.html")