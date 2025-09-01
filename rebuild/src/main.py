import asyncio
import logging
import os
import ssl
import tempfile
import threading
import uuid

import aiodbm
from aiohttp import web
from aiohttp.web import Response, json_response
from werkzeug.utils import secure_filename

from logging_config import setup_logging
from service.processor import process, process_from_files, process_player_team
from service.registry import save, get_by_id, load
from service.videos import create_videos_app  
from service.dbm_service import init_db, db_get, db_set
from service.register import update_status, get_status, create_register_app

from streaming_server import create_stream_server

setup_logging()

logger = logging.getLogger(__name__)

# load existing registrations
load()

# SSL config
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile='./certs/selfsigned.crt', keyfile='./certs/selfsigned.key')

# --- Routes ---


async def check_progress(request: web.Request) -> web.Response:
    video_id = request.match_info['video_id']
    logger.info(f"video id {video_id}")
    register = request.app["register"]
    status = register.get_status(video_id)
    # registration = get_by_id(registration_id)
    if status is None:
        return json_response({'status': 'not_found'}, status=404)
        # return json_response({'status': registration['status']})
    return json_response({'status': status})


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

async def create_app():
    app = web.Application(client_max_size=100 * 1024 ** 2)  # 100MB limit

    # app.router.add_post('/upload', upload_video)
    app.router.add_get('/{registration_id}/status', check_progress)
    app.router.add_get('/{registration_id}', retrieve_player_teams)
    app.router.add_get('/{registration_id}/player/{player_id}', retrieve_player_picture)
    app.router.add_get('/', serve_index)
    app.router.add_get('/{path:.*}', serve_static)

    # add the db
    # db = await init_db(app,"dbm","./data/videos.dbm")
    db = await aiodbm.open("./data/videos.dbm", "c")
    # register = await init_db(app,"register","./data/register.dbm")
    register = await aiodbm.open("./data/register.dbm", "c")

    # Mount videos sub-app
    app.add_subapp('/api/v1/videos', create_videos_app(db))

    # add the register
    app.add_subapp('/api/v1/status',create_register_app(register))

    # add the streaming server
    app.add_subapp('/api/v1/stream',create_stream_server())
    
    return app


if __name__ == '__main__':
    web.run_app(create_app(), host="0.0.0.0", port=8443, ssl_context=ssl_context)
