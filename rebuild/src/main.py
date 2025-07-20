
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import logging
import os
import tempfile
import threading

from logging_config import setup_logging
from service.processor import process, process_from_files, process_player_team
from service.registry import save, get_by_id, load

setup_logging()


app = Flask(__name__)
app.logger.handlers = logging.getLogger().handlers
app.logger.setLevel(logging.INFO)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100MB

# setup logging
logger = logging.getLogger(__name__)

# load the registrations
load()

@app.route('/upload',methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file'] # get the video
    if file.filename == '':
        return 'No selected file',400
    # create a file name
    filename = secure_filename(file.filename)
    # save
    with tempfile.NamedTemporaryFile(delete=False,suffix=os.path.splitext(filename)[1]) as temp_file:
        file.save(temp_file)
        temp_path = temp_file.name

    # register
    registration_id = save(filename)
    frame_location = f"./frame.{registration_id}.pkl"
    track_location = f"./tracks.{registration_id}.pkl"
    teams_location = f"./teams.{registration_id}.pkl"
    ball_location = f"./ball.{registration_id}.pkl"
    # process
    thread = threading.Thread(target=process,args=(temp_path,registration_id,frame_location,track_location,ball_location,teams_location,))
    thread.daemon = True
    thread.start()

    return jsonify({'registrationId':registration_id}),200
    # return f'Saved {registration_id}',200

@app.route('/<registration_id>/status',methods=['GET'])
def check_progress(registration_id):
    logger.info(f"registration id {registration_id}")
    registration = get_by_id(registration_id)
    if registration is None:
        return jsonify({'status':'not_found'}),404
    # need to check the status
    return jsonify({'status':registration['status']}),200
    # if is_running:
    #     return jsonify({'status':'still_processing'}),200
    # return jsonify({'status':'complete'}),200

@app.route('/<registration_id>',methods=['GET'])
def retrieve_player_teams(registration_id):
    logger.info(f"registration id {registration_id}")
    registration = get_by_id(registration_id)
    if registration is None:
        return jsonify({'status':'not_found'}),404
    # get the player - to - team processing    
    return process_player_team(registration_id)

@app.route('/<registration_id>/player/<player_id>',methods=['GET'])
def retrieve_player_picture(registration_id,player_id):
    logger.info(f" registration {registration_id} player id {player_id}")
    # look up the array and get the image

if __name__ == "__main__":
    # start the app
    app.run(host="0.0.0.0",port=5000)

    

