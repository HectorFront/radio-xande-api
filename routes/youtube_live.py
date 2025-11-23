from flask import Blueprint, request
from flask_socketio import emit
from app.applications import app, socketio
from controller.youtube_live import YouTubeLiveControl
from services.youtube_live import YouTubeLiveService
from domain.youtube import YT_CHANNEL_ID_SUPERXANDAO

youtube_live_bp = Blueprint('youtube_live', __name__)
youtube_service = YouTubeLiveService()

@youtube_live_bp.route('/api/v1/user/youtube/live/superxandao', methods=['GET'])
def get_live_status():
    return YouTubeLiveControl.get_live_status()

@youtube_live_bp.route('/api/v1/user/youtube/chat/superxandao', methods=['GET'])
def get_chat_messages():
    return YouTubeLiveControl.get_chat_messages(request)

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    emit('connected', {'status': 'Connected to YouTube Live service'})

@socketio.on('disconnect')
def handle_disconnect():
    youtube_service.stop_chat_monitoring()

@socketio.on('start_monitoring')
def handle_start_monitoring():
    try:
        youtube_service.start_chat_monitoring(socketio)
        emit('monitoring_started', {'channel_id': YT_CHANNEL_ID_SUPERXANDAO})
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('stop_monitoring')
def handle_stop_monitoring():
    youtube_service.stop_chat_monitoring()
    emit('monitoring_stopped', {'status': 'Monitoring stopped'})

app.register_blueprint(youtube_live_bp)