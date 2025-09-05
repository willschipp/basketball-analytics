import logging
import uuid

logger = logging.getLogger(__name__)

movie_register = []

# status
# 'new'
# 'getting frames'
# 'getting players'
# 'getting possessions'

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
    logger.debug(registration_id)
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



