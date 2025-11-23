from model.ad import AdModel
from schema.ad import AdSchema 
from domain.http_response import HttpResponse

class AdControl:
    
    @staticmethod
    def get_ad():
        ad = AdModel.get_ad()
        if ad:
            return {
                "description": ad.description,
                "description_url": ad.description_url,
                "url_attached": ad.url_attached
            }
        return HttpResponse.not_found()