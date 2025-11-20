from app import app, client_required
from flask import request
from controller import MusicControl

@app.route("/api/v1/user/post/create/music", methods=["POST"])
@client_required
def create_music():
    return MusicControl.create_music(request)

@app.route("/api/v1/user/post/music/<music_id>", methods=["GET", "PUT", "PATCH",])
@client_required
def get_music(music_id):
    if request.method == "GET":
        return MusicControl.get_music(music_id)
    elif request.method in ["PUT", "PATCH"]:
        return MusicControl.update_music(request, music_id)

@app.route("/api/v1/user/post/music", methods=["GET"])
@client_required
def get_all_music():
    return MusicControl.get_all_music()