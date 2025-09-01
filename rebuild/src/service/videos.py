from aiohttp import web
from datetime import datetime

routes = web.RouteTableDef()

@routes.get('')
async def list_videos(request: web.Request):
    # Example response to list videos
    current_date = datetime.now().isoformat()
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
    return web.json_response(videos)


@routes.get('/{video_id}')
async def get_video(request: web.Request):
    video_id = request.match_info['video_id']
    current_date = datetime.now().isoformat()
    video = {
        "id": int(video_id),
        "title": f"Video {video_id}",
        "timestamp": current_date,
    }
    return web.json_response(video)


def create_videos_app():
    """
    This replaces the Flask Blueprint.
    Mount it as a sub-application at /api/v1/videos
    """
    app = web.Application()
    app.add_routes(routes)
    return app
