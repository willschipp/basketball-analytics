import aiodbm
from aiohttp import web
import logging

logger = logging.getLogger(__name__)

routes = web.RouteTableDef()

DB_FILE = "./data/register.dbm"

async def update_status(video_id,msg):
    # retrieve the db
    db = await aiodbm.open(DB_FILE,"c")
    # get the id
    current_state = await db.get(video_id)
    if current_state:
        # log the current state
        logger.info(f"changing {video_id} from {current_state} to {msg}")    
    # update the status
    await db.set(video_id,msg)

@routes.get('/{video_id}')
async def get_status(request: web.Request):
    video_id = request.match_info['video_id']
    # retrieve and return the status
    db = await aiodbm.open(DB_FILE,"c")
    # db = request.app["register"]
    # get the id
    current_state = await db.get(video_id)

    # validate
    if current_state:
        return web.json_response({"currentState": current_state})
    else:
        return web.json_response({})

def create_register_app(shared_dbm):
    # init    
    app = web.Application()
    # setup the database
    app['register'] = shared_dbm
    # add the routes
    app.add_routes(routes)
    return app        