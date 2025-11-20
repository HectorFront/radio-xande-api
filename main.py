from app.applications import database, app, socketio
from routes import *

if __name__ == "__main__":
    with app.app_context():
        database.create_all()
        socketio.run(app, host='0.0.0.0', port=8080, debug=False)