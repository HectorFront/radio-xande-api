from flask import Blueprint, request, jsonify
from flask_socketio import emit
from app.applications import app, socketio
from services.youtube_live import YouTubeLiveService

youtube_live_bp = Blueprint('youtube_live', __name__)
youtube_service = YouTubeLiveService()

@youtube_live_bp.route('/api/v1/user/youtube/live/<channel_id>', methods=['GET'])
def get_live_status(channel_id):
    try:
        status = youtube_service.get_channel_live_status(channel_id)
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@youtube_live_bp.route('/api/v1/user/youtube/chat/<live_chat_id>', methods=['GET'])
def get_chat_messages(live_chat_id):
    try:
        page_token = request.args.get('pageToken')
        youtube_service.live_chat_id = live_chat_id
        
        messages = youtube_service.get_live_chat_messages(page_token)
        return jsonify(messages), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    emit('connected', {'status': 'Connected to YouTube Live service'})

@socketio.on('disconnect')
def handle_disconnect():
    youtube_service.stop_chat_monitoring()

@socketio.on('start_monitoring')
def handle_start_monitoring(data):
    channel_id = data.get('channel_id')
    
    if not channel_id:
        emit('error', {'message': 'channel_id is required'})
        return
    
    try:
        youtube_service.start_chat_monitoring(socketio, channel_id)
        emit('monitoring_started', {'channel_id': channel_id})
        
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('stop_monitoring')
def handle_stop_monitoring():
    youtube_service.stop_chat_monitoring()
    emit('monitoring_stopped', {'status': 'Monitoring stopped'})

app.register_blueprint(youtube_live_bp)