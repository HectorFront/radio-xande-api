import uuid
from model import MusicModel
from helpers import FieldsHelper
from domain.http_response import HttpResponse
from services import S3UploadService, S3UploadException, MediaStreamService

class MusicControl:
    
    fields_optional = ["file_image"]
    
    @staticmethod
    def create_music(request):
        try:
            description = request.form.get('description')
            file_music = request.files.get('file_music')
            file_image = request.files.get('file_image')
            if not description or not file_music:
                return HttpResponse.bad_request(message="Description and file music are required")
            filename_image = None
            filename_music = f"music_{uuid.uuid4()}.mp3"
            if file_image:
                filename_image = f"image_{uuid.uuid4()}.png"
                if file_image.content_type.startswith('image/'):
                    image_attached = S3UploadService.upload_image(file_image, filename_image)
                else:
                    return HttpResponse.bad_request(message="file_image must be image")
            if file_music.content_type.startswith('audio/'):
                duration_ms = MediaStreamService.get_duration_ms(file_music)
                url_attached = S3UploadService.upload_audio(file_music, filename_music)
            else:
                return HttpResponse.bad_request(message="file_music must be audio")
            music = MusicModel.insert(description, url_attached, image_attached, duration_ms=duration_ms)
            MusicModel.commit()
            return HttpResponse.created_successfully({
                "id": music.id,
                "description": music.description,
                "filename_music": filename_music,
                "filename_image": filename_image
            })
        except S3UploadException as e:
            return e.response
        except Exception as e:
            MusicModel.rollback()
            return HttpResponse.internal_server_error(message=str(e))
        
    @staticmethod
    def get_music(music_id):
        try:
            music = MusicModel.get_by_id(music_id)
            if not music:
                return HttpResponse.not_found(message="Music not found")
            filename_music = music.url_attached.split('/')[-1]
            filename_image = music.image_attached.split('/')[-1] if music.image_attached else None
            return HttpResponse.ok({
                "id": music.id,
                "description": music.description,
                "filename_music": filename_music,
                "filename_image": filename_image,
                "duration_ms": music.duration_ms
            })
        except Exception as e:
            return HttpResponse.internal_server_error(message=str(e))
    
    @staticmethod
    def update_music(request, music_id):
        try:
            data = request.form
            new_file_image = request.files.get('file_image')
            music = MusicModel.get_by_id(music_id)
            image_attached = music.image_attached
            if not music:
                return HttpResponse.not_found(message="Music not found")
            if new_file_image:
                if image_attached:
                    S3UploadService.delete_file(music.image_attached.split('/')[-1])
                new_filename_image = f"image_{uuid.uuid4()}.png"
                if new_file_image.content_type.startswith('image/'):
                    image_attached = S3UploadService.upload_image(new_file_image, new_filename_image)
                else:
                    return HttpResponse.bad_request(message="File image must be image")
            update = {
                "description": data.get('description', music.description),
                "image_attached": image_attached
            }
            for key, value in update.items():
                if FieldsHelper.is_valid_field_with_optional_fields(key, value, MusicControl.fields_optional):
                    MusicModel.update(music, key, value)
            MusicModel.commit()
            return HttpResponse.ok()
        except Exception as e:
            return HttpResponse.internal_server_error(message=str(e))
    
    @staticmethod
    def get_all_music():
        try:
            musics = MusicModel.get_all()
            return HttpResponse.ok([{
                "id": music.id,
                "description": music.description,
                "filename_music": music.url_attached.split('/')[-1],
                "filename_image": music.image_attached.split('/')[-1] if music.image_attached else None,
                "duration_ms": music.duration_ms
            } for music in musics])
        except Exception as e:
            return HttpResponse.internal_server_error(message=str(e))