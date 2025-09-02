import aiodbm
from aiohttp import web
import asyncio
import janus
import logging

logger = logging.getLogger(__name__)

routes = web.RouteTableDef()

DB_FILE = "./data/register.dbm"

async def update_status(app,video_id,msg):
    async with app['lock']:
        db = app['register']
        await db.set(video_id,msg)

@routes.get('/{video_id}')
async def get_status(request: web.Request):
    video_id = request.match_info['video_id']
    # retrieve and return the status
    async with request.app['lock']:
        db = request.app['register']
        current_state = await db.get(video_id)
    # validate
    if current_state:
        # convert
        current_state_str = current_state.decode("utf-8")
        return web.json_response({"currentState": current_state_str})
    else:
        return web.json_response({})

async def queue_processor(app):
    q = app['janus'].async_q
    while True:
        video_id, msg = await q.get()
        await update_status(app,video_id,msg)
        q.task_done()

async def on_startup(app):
    app['register'] = await aiodbm.open(DB_FILE,'c')
    app['lock'] = asyncio.Lock()
    app['janus'] = janus.Queue()
    app['queue_task'] = asyncio.create_task(queue_processor(app)) # this sets up the scaffolding
    return app

async def on_cleanup(app):
    await app['register'].close()
    await app['janus'].aclose()
    app['queue_task'].cancel()

async def create_register_app(shared_dbm):
    # init    
    app = web.Application()
    # setup the database
    app['register'] = shared_dbm
    # add the routes
    app.add_routes(routes)
    app = await on_startup(app)
    # app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    # return
    return app        