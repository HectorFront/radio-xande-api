from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_socketio import SocketIO
from infra import env, allowed_origin, DumpSQL, FirewallRequestMiddleware

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqlconnector://{env.get('CONN_MYSQL_USER_DEV')}"
    app.config["SECRET_KEY"] = "SECRET"
    app.config['SQLALCHEMY_ECHO'] = False
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    CORS(app, resources={r"/api/v1/user/*": {"origins": allowed_origin }})
    app.wsgi_app = FirewallRequestMiddleware(app.wsgi_app)
    return app

app = create_app()
database = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
# dump_sql = DumpSQL().start()
migrate = Migrate(app, database, render_as_batch=True)
serializer = Marshmallow(app)