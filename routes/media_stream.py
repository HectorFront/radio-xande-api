from app import app
from services.media_stream import MediaStreamService

@app.route('/api/v1/user/stream/media/<filename>')
def stream_media(filename):
    return MediaStreamService.stream_media(filename)