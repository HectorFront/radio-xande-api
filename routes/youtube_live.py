from flask import request
from flask_socketio import emit
from app.applications import app, socketio
from controller import YouTubeLiveControl
from services.service_registry import ServiceRegistry
from domain.youtube import YT_CHANNEL_ID_SUPERXANDAO

@app.route('/api/v1/user/youtube/live/superxandao', methods=['GET'])
def get_live_yt__status():
    return YouTubeLiveControl.get_live_status()

@app.route('/api/v1/user/youtube/chat/superxandao', methods=['GET'])
def get_chat_yt_messages():
    return YouTubeLiveControl.get_chat_messages(request)

# WebSocket Events
@socketio.on('connect')
def handle_yt_connect():
    emit('connected', {'status': 'Connected to YouTube Live service'})

@socketio.on('disconnect')
def handle_yt_disconnect():
    youtube_service = ServiceRegistry.get_youtube_service()
    youtube_service.stop_chat_monitoring()

@socketio.on('start_monitoring')
def handle_start_yt_monitoring():
    try:
        youtube_service = ServiceRegistry.get_youtube_service()
        youtube_service.start_chat_monitoring(socketio)
        emit('monitoring_started', {'channel_id': YT_CHANNEL_ID_SUPERXANDAO})
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('stop_monitoring')
def handle_stop_yt_monitoring():
    youtube_service = ServiceRegistry.get_youtube_service()
    youtube_service.stop_chat_monitoring()
    emit('monitoring_stopped', {'status': 'Monitoring stopped'})