from flask import Blueprint, jsonify
from datetime import datetime

videos_bp = Blueprint('videos', __name__, url_prefix='/api/v1/videos')

@videos_bp.route('/', methods=['GET'])
def list_videos():
    # Example response to list videos
    current_date = datetime.now()
    videos = [
      {
        "id": 1,
        "title": "Video 1",
        "url": "/video-1",
        "timestamp": current_date,
      },
      {
        "id": 2,
        "title": "Video 2",
        "url": "/video-2",
        "timestamp": current_date,
      },
    ]
    return jsonify(videos)

@videos_bp.route('/<video_id>', methods=['GET'])
def get_video(video_id):
    current_date = datetime.now()
    video = {
        "id": 1,
        "title": "Video 1",
        "timestamp": current_date
      }
    return jsonify(video)
