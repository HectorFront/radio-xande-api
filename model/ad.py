from schema.ad import Ad

class AdModel:

    @staticmethod
    def get_ad() -> object:
        return Ad.query.one()