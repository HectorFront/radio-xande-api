from app import database, serializer

class Ad(database.Model):
    __tablename__ = "ad"

    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    description = database.Column(database.String(500), nullable=False)
    description_url = database.Column(database.String(100), nullable=True)
    url_attached = database.Column(database.Text, nullable=True)

class AdSchema(serializer.SQLAlchemyAutoSchema):
    class Meta:
        model = Ad
