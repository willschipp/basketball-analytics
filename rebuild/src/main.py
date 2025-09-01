import asyncio
import logging
import os
import ssl
import tempfile
import threading
import uuid

from aiohttp import web
from aiohttp.web import Response, json_response
from werkzeug.utils import secure_filename

from logging_config import setup_logging
from service.processor import process, process_from_files, process_player_team
from service.registry import save, get_by_id, load
from service.videos import create_videos_app  # if videos_bp is Flask blueprint, will need refactor

from streaming_server import create_stream_server

setup_logging()

logger = logging.getLogger(__name__)

# load existing registrations
load()

# SSL config
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile='./certs/selfsigned.crt', keyfile='./certs/selfsigned.key')

# --- Routes ---

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
    registration_id = save(filename)
    frame_location = f"./frame.{registration_id}.pkl"
    track_location = f"./tracks.{registration_id}.pkl"
    teams_location = f"./teams.{registration_id}.pkl"
    ball_location = f"./ball.{registration_id}.pkl"

    # process in background thread
    def _process():
        process(temp_path, registration_id, frame_location, track_location, ball_location, teams_location)
    thread = threading.Thread(target=_process, daemon=True)
    thread.start()

    return json_response({'registrationId': registration_id})


async def check_progress(request: web.Request) -> web.Response:
    registration_id = request.match_info['registration_id']
    logger.info(f"registration id {registration_id}")
    registration = get_by_id(registration_id)
    if registration is None:
        return json_response({'status': 'not_found'}, status=404)
    return json_response({'status': registration['status']})


async def retrieve_player_teams(request: web.Request) -> web.Response:
    registration_id = request.match_info['registration_id']
    logger.info(f"registration id {registration_id}")
    registration = get_by_id(registration_id)
    if registration is None:
        return json_response({'status': 'not_found'}, status=404)
    return await process_player_team(registration_id) \
           if asyncio.iscoroutinefunction(process_player_team) \
           else process_player_team(registration_id)


async def retrieve_player_picture(request: web.Request) -> web.Response:
    registration_id = request.match_info['registration_id']
    player_id = request.match_info['player_id']
    logger.info(f" registration {registration_id} player id {player_id}")
    # TODO: implement logic returning web.FileResponse or binary Response
    return web.Response(text="Not implemented", status=501)


async def serve_index(request: web.Request) -> web.Response:
    return web.FileResponse('./ux/dist/index.html')


async def serve_static(request: web.Request) -> web.Response:
    path = request.match_info['path']
    return web.FileResponse(f'./ux/dist/{path}')


# --- Setup App ---

def create_app():
    app = web.Application(client_max_size=100 * 1024 ** 2)  # 100MB limit

    app.router.add_post('/upload', upload_video)
    app.router.add_get('/{registration_id}/status', check_progress)
    app.router.add_get('/{registration_id}', retrieve_player_teams)
    app.router.add_get('/{registration_id}/player/{player_id}', retrieve_player_picture)
    app.router.add_get('/', serve_index)
    app.router.add_get('/{path:.*}', serve_static)

    # Mount videos sub-app
    app.add_subapp('/api/v1/videos', create_videos_app())

    # add the streaming server
    app.add_subapp('/api/v1/stream',create_stream_server())

    return app


if __name__ == '__main__':
    web.run_app(create_app(), host="0.0.0.0", port=8443, ssl_context=ssl_context)
