import aiodbm
import aiofiles
import asyncio
from aiohttp import web
from datetime import datetime
import json
import logging
import os
import shutil
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
    videos = []
    keys = await db.keys()
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
    video_id = uuid.uuid4()
    video_id = str(video_id) # convert
    # create the video object and save
    video = {
        "id": video_id,
        "title": "",
        "timestamp": datetime.now().isoformat(),
        "url": f"{video_id}{suffix}"
    }
    dest_path = os.path.join("data",f"{video_id}{suffix}")
    shutil.copy(temp_path,dest_path) # creates a copy --> this is used for streaming back
    # save
    db = request.app["dbm"]
    video_json = json.dumps(video)
    await db.set(video_id,video_json) # wait for it to write
    logger.info(f"have written {video_id} to the database file as a {video_json}")

    # setup locations
    frame_location = f"./data/frame.{video_id}.pkl"
    track_location = f"./data/tracks.{video_id}.pkl"
    teams_location = f"./data/teams.{video_id}.pkl"
    ball_location = f"./data/ball.{video_id}.pkl"

    # get the queue for status
    q = request.app['janus']

    # process in background thread
    def _process():
        process(temp_path, q, video_id, frame_location, track_location, ball_location, teams_location)
    thread = threading.Thread(target=_process, daemon=True)
    thread.start()

    return web.json_response({'videoId': video_id})

@routes.get('/{video_id}/stream')
async def stream_video(request):
    video_id = request.match_info['video_id']
    db = request.app["dbm"]
    video_value = await db.get(video_id)
    video = json.loads(video_value)
    url = video['url']
    uri = f"./data/{url}"
    logger.info(f"Streaming video at {uri}")

    # if the files not there, bail
    if not os.path.exists(uri):
        return web.Response(text="Video not found", status=404)

    #get the file size
    file_size = os.path.getsize(uri)

    range_header = request.headers.get("Range", None)
    start = 0
    end = file_size - 1

    if range_header:
        # Parse the Range header. Example: "bytes=0-1023"
        range_match = None
        import re
        range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if range_match:
            start = int(range_match.group(1))
            if range_match.group(2):
                end = int(range_match.group(2))
        if end >= file_size:
            end = file_size - 1
        length = end - start + 1

        # Prepare Streaming Response with 206 Partial Content
        resp = web.StreamResponse(
            status=206,
            headers={
                "Content-Type": "video/mp4",
                "Content-Length": str(length),
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Disposition": f'inline; filename="{url}"'
            }
        )
    else:
        # No range header, send full content with 200 OK
        length = file_size
        resp = web.StreamResponse(
            status=200,
            headers={
                "Content-Type": "video/mp4",
                "Content-Length": str(length),
                "Accept-Ranges": "bytes",
                "Content-Disposition": f'inline; filename="{url}"'
            }
        )

    await resp.prepare(request)

    try:
        async with aiofiles.open(uri, "rb") as f:
            await f.seek(start)
            chunk_size = 8192
            bytes_remaining = length
            while bytes_remaining > 0:
                read_size = min(chunk_size, bytes_remaining)
                chunk = await f.read(read_size)
                if not chunk:
                    break
                await resp.write(chunk)
                bytes_remaining -= len(chunk)
    except (ConnectionResetError, asyncio.CancelledError) as e:
        # Client disconnected during streaming
        pass
    except Exception as e:
        # Log other errors
        logger.error(f"Error while streaming video: {e}")
    finally:
        try:
            await resp.write_eof()
        except Exception:
            pass

    return resp


def create_videos_app(shared_dbm,q):
    # init    
    app = web.Application()
    # setup the database
    app['dbm'] = shared_dbm
    app['janus'] = q
    # add the routes
    app.add_routes(routes)
    return app
