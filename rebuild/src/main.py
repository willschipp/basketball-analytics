# from utils.frame_tools import save_frames,get_frames
# from detector.players import detect_players
# from detector.team import get_team_assignment
# from detector.ball import detect_ball, remove_wrong_detections, refine, detect_possession

# import pickle

# import logging

# from logging_config import setup_logging

# def process_frames_to_tracks_stream(frame_location,track_location):
#     with open(frame_location,'rb') as frames_in, open(track_location,'wb') as tracks_out:
#         while True:
#             try:
#                 logger.info("loading a batch: frames to tracks")
#                 frames = pickle.load(frames_in) # get a batch
#                 tracks = detect_players(frames)
#                 pickle.dump(tracks,tracks_out)
#                 logger.info("written a batch")
#             except EOFError:
#                 break

# def process_frames_for_ball_stream(frame_location,ball_location):
#     with open(frame_location,'rb') as frames_in, open(ball_location,'wb') as tracks_out:
#         while True:
#             try:
#                 logger.info("loading a batch: ball location")
#                 frames = pickle.load(frames_in) # get a batch
#                 balls = detect_ball(frames)
#                 balls = remove_wrong_detections(balls)
#                 balls = refine(balls)
#                 pickle.dump(balls,tracks_out)
#                 logger.info("written a batch")
#             except EOFError:
#                 break       

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import logging
import os
import tempfile
import threading

from logging_config import setup_logging
from service.processor import process, process_from_files, process_player_team
from service.registry import save,get_by_id

setup_logging()

app = Flask(__name__)
app.logger.handlers = logging.getLogger().handlers
app.logger.setLevel(logging.INFO)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100MB

logger = logging.getLogger(__name__)

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
    # process
    thread = threading.Thread(target=process,args=(temp_path,registration_id,))
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


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)
    # process_from_files()

# if __name__ == "__main__":
#     setup_logging()
#     logger = logging.getLogger(__name__)
#     # save it to a file
#     # logger.info("loading frames")
#     # save_frames('./samples/video_1.mp4','./frames.pkl')
#     # save_frames('./samples/Segment_00000.mov','./frames.mov.pkl')
#     # detect players
#     logger.info("using frames to generate tracks")
#     frames = get_frames('./frames.mov.pkl')
#     process_frames_to_tracks_stream('./frames.mov.pkl','tracks.pkl')
#     logger.info("complete... now using tracks to get players")

#     # tracks = get_frames('./tracks.pkl')
#     # player_ids = []
#     # for track in tracks:
#     #     for key in track:
#     #         if key not in player_ids:
#     #             player_ids.append(key)
#     # # tracks = detect_players(frames)
#     # have a bunch of players, now lets get their touches
#     # player_assignments = []
#     # player_assignments = get_team_assignment(frames,tracks,"white shirt","dark blue shirt")
#     # # save the player assignments
#     # with open('./teams.pkl','wb') as f:
#     #     pickle.dump(player_assignments,f)
#     # we now have
#     # - frames in a pkl
#     # - players and their tracks in a pkl
#     # - player-to-team in a pkl
#     # let's do some ball work
#     logger.info("starting to process ball positions")
#     process_frames_for_ball_stream('./frames.mov.pkl','./balls.pkl')
#     logger.info("complete")
#     # clean up the tracks
#     # TODO move into the streaming process
#     # ball_tracks = get_frames('./balls.pkl')
#     # process
#     # ball_tracks = remove_wrong_detections(ball_tracks)
#     # # check again
#     # ball_tracks = refine(ball_tracks)
#     # get the acquisitions
#     # logger.info("starting to process ball possessions")
#     # ball_possessions = detect_possession(tracks,ball_tracks)
#     # logger.info(ball_possessions)


    
    

