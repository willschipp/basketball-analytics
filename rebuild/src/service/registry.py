import logging
import uuid

from utils.file_tools import get_registration_ids

logger = logging.getLogger(__name__)

movie_register = []

# status
# 'new'
# 'getting frames'
# 'getting players'
# 'getting possessions'

def load():
    # load up any existing registrations
    ids = get_registration_ids()
    for id in ids:
        movie_registration = {
            'registration_id': id,
            'file_location': "",
            'status':'complete'
        }        
        movie_register.append(movie_registration)
        logger.info(f"added {id}")


def save(file_name):
    registration_uuid = uuid.uuid4()
    movie_registration = {
        'registration_id': str(registration_uuid),
        'file_location': file_name,
        'status':'new'
    }
    # save
    movie_register.append(movie_registration)
    # return
    return str(registration_uuid)

def get_by_id(registration_id):
    logger.info(registration_id)
    if len(movie_register) <= 0:
        load() # just in case
    for _,movie_registration in enumerate(movie_register):
        if movie_registration['registration_id'] == registration_id:
            return movie_registration
    return None #oops

def update_status(registration_id,status):
    for idx,movie_registration in enumerate(movie_register):
        if movie_registration['registration_id'] == registration_id:
            logger.debug(f"updating status for {registration_id} to {status}")
            movie_registration['status'] = status
            return # nothing more to be done



