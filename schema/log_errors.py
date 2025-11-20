from app import database, serializer

class LogErrors(database.Model):
    __tablename__ = "log_errors"

    id = database.Column(database.Integer, primary_key=True, nullable=False, autoincrement=True)
    url = database.Column(database.Text, nullable=True)
    options = database.Column(database.Text, nullable=True)
    status_code = database.Column(database.Integer, nullable=True)
    status_text = database.Column(database.Text, nullable=True)
    error = database.Column(database.Text, nullable=True)

class LogErrorsSchema(serializer.SQLAlchemyAutoSchema):
    class Meta:
        model = LogErrors