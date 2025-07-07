from detector.ball import detect_ball, remove_wrong_detections, refine, detect_possession, detect_passes, detect_interceptions
from detector.players import detect_players
from detector.team import get_team_assignment
from utils.frame_tools import save_frames
from utils.file_tools import get_list
from service.registry import update_status

import pickle

import logging

logger = logging.getLogger(__name__)

team_1_class_name = "white shirt"
team_2_class_name = "dark blue shirt"

def process(video_location,registration_id,frame_location="./frames.pkl",track_location="./tracks.pkl",ball_location="./ball.pkl",teams_location="./teams.pkl"):
    logging.info("starting to process video to frames")
    update_status(registration_id,"getting frames")
    save_frames(video_location,frame_location)
    logging.info("done")
    logging.info("starting to process frames to player tracks")
    update_status(registration_id,"getting players")
    process_frames_to_tracks_stream(frame_location,track_location,teams_location)
    logging.info("done")
    logging.info("starting to process frames to ball tracks")
    update_status(registration_id,"getting possessions")
    process_frames_for_ball_stream(frame_location,ball_location)
    logging.info("done")
    # now we have the ball track and player tracks, get the stats together
    player_tracks = get_list(track_location)
    ball_tracks = get_list(ball_location)
    team_tracks = get_list(teams_location)
    # get teams
    possession_list = detect_possession(player_tracks,ball_tracks)
    # possession list shows who had possession of the ball (player_id) in each frame
    passes = detect_passes(possession_list,team_tracks)
    interceptions = detect_interceptions(possession_list,team_tracks)

    


def process_frames_to_tracks_stream(frame_location,track_location,teams_location):
    with open(frame_location,'rb') as frames_in, open(track_location,'wb') as tracks_out, open(teams_location,'wb') as teams_out:
        while True:
            try:
                logger.info("loading a batch: frames to tracks")
                frames = pickle.load(frames_in) # get a batch
                tracks = detect_players(frames)
                pickle.dump(tracks,tracks_out)
                assignments = get_team_assignment(frames,tracks,team_1_class_name,team_2_class_name)
                pickle.dump(assignments,teams_out)
                logger.info("written a batch")
            except EOFError:
                break

def process_frames_for_ball_stream(frame_location,ball_location):
    with open(frame_location,'rb') as frames_in, open(ball_location,'wb') as tracks_out:
        while True:
            try:
                logger.info("loading a batch: ball location")
                frames = pickle.load(frames_in) # get a batch
                balls = detect_ball(frames)
                balls = remove_wrong_detections(balls)
                # balls = refine(balls) TODO fix
                pickle.dump(balls,tracks_out)
                logger.info("written a batch")
            except EOFError:
                break       