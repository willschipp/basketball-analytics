import logging
import os
import pickle

logger = logging.getLogger(__name__)

def get_list(pkl_path):
    values = []
    with open(pkl_path,'rb') as f:
        values = pickle.load(f)    
    return values

def get_registration_ids():
    files = []
    directory = os.path.abspath("./") # root path
    logger.info(directory)
    for filename in os.listdir(directory):
        if filename.endswith(".pkl") and os.path.isfile(os.path.join(directory,filename)):
            # got it, now need to extract the id
            parts = filename.split(".")
            if len(parts) == 3:
                # this is registration pkl
                if parts[1] not in files:
                    files.append(parts[1])
                    logger.info(f"found {parts[1]}")
    return files