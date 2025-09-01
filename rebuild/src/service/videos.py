import aiodbm
from aiohttp import web
from datetime import datetime
import json
import logging
import os
import tempfile
import threading
import uuid

from werkzeug.utils import secure_filename

from service.processor import process, process_from_files, process_player_team
from service.register import update_status, get_status

logger = logging.getLogger(__name__)

routes = web.RouteTableDef()

DB_FILE = "./data/videos.dbm"

@routes.get('')
async def list_videos(request: web.Request):
    # open up the database
    db = request.app["dbm"] #get the database
        # retrieve the db
    # db = await aiodbm.open(DB_FILE,"c")
    videos = []
    keys = await db.keys()
    logger.info(keys)
    for key in keys:
        value = await db.get(key) # load the value (json string)
        # convert back
        video = json.loads(value)
        videos.append(video)
    return web.json_response(videos)

@routes.get('/{video_id}')
async def get_video(request: web.Request):
    video_id = request.match_info['video_id']
    # open up the database
    db = request.app["dbm"]
    # db = await aiodbm.open(DB_FILE,"c")
    video_value = await db.get(video_id)
    video = json.loads(video_value)
    return web.json_response(video)

# upload the video and start the processing
@routes.post('')
async def upload_video(request: web.Request) -> web.Response:
    reader = await request.multipart()
    field = await reader.next()
    if not field or field.name != 'file':
        return web.Response(text='No file part', status=400)

    filename = field.filename
    if not filename:
        return web.Response(text="No selected file", status=400)

    filename = secure_filename(filename)
    suffix = os.path.splitext(filename)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        size = 0
        while True:
            chunk = await field.read_chunk()  # async chunk read
            if not chunk:
                break
            temp_file.write(chunk)
            size += len(chunk)
        temp_path = temp_file.name

    # register
    # registration_id = save(filename)
    video_id = uuid.uuid4()
    video_id = str(video_id) # convert
    # create the video object and save
    video = {
        "id": video_id,
        "title": "",
        "timestamp": datetime.now().isoformat()
    }
    # save
    db = request.app["dbm"]
    # db = await aiodbm.open(DB_FILE,"c")
    video_json = json.dumps(video)
    await db.set(video_id,video_json) # wait for it to write
    logger.info(f"have written {video_id} to the database file as a {video_json}")

    # setup locations
    frame_location = f"./data/frame.{video_id}.pkl"
    track_location = f"./data/tracks.{video_id}.pkl"
    teams_location = f"./data/teams.{video_id}.pkl"
    ball_location = f"./data/ball.{video_id}.pkl"

    # process in background thread
    def _process():
        process(temp_path, video_id, frame_location, track_location, ball_location, teams_location)
    thread = threading.Thread(target=_process, daemon=True)
    thread.start()

    return web.json_response({'videoId': video_id})


def create_videos_app(shared_dbm):
    # init    
    app = web.Application()
    # setup the database
    app['dbm'] = shared_dbm
    # add the routes
    app.add_routes(routes)
    return app
