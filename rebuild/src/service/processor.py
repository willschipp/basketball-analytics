from detector.ball import detect_ball, remove_wrong_detections, refine
from detector.players import detect_players
from utils.frame_tools import save_frames
from service.registry import update_status

import pickle

import logging

logger = logging.getLogger(__name__)

def process(video_location,registration_id,frame_location="./frames.pkl",track_location="./tracks.pkl",ball_location="./ball.pkl"):
    logging.info("starting to process video to frames")
    update_status(registration_id,"getting frames")
    save_frames(video_location,frame_location)
    logging.info("done")
    logging.info("starting to process frames to player tracks")
    update_status(registration_id,"getting players")
    process_frames_to_tracks_stream(frame_location,track_location)
    logging.info("done")
    logging.info("starting to process frames to ball tracks")
    update_status(registration_id,"getting possessions")
    process_frames_for_ball_stream(frame_location,ball_location)
    logging.info("done")

def process_frames_to_tracks_stream(frame_location,track_location):
    with open(frame_location,'rb') as frames_in, open(track_location,'wb') as tracks_out:
        while True:
            try:
                logger.info("loading a batch: frames to tracks")
                frames = pickle.load(frames_in) # get a batch
                tracks = detect_players(frames)
                pickle.dump(tracks,tracks_out)
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
                balls = refine(balls)
                pickle.dump(balls,tracks_out)
                logger.info("written a batch")
            except EOFError:
                break       