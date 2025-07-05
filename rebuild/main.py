from utils.frame_tools import save_frames,get_frames
from detector.players import detect_players
from detector.team import get_team_assignment
from detector.ball import detect_ball

import pickle

import logging

from logging_config import setup_logging

def process_frames_to_tracks_stream(frame_location,track_location):
    with open(frame_location,'rb') as frames_in, open(track_location,'wb') as tracks_out:
        while True:
            try:
                logger.info("loading a batch")
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
                logger.info("loading a batch")
                frames = pickle.load(frames_in) # get a batch
                balls = detect_ball(frames)
                pickle.dump(balls,tracks_out)
                logger.info("written a batch")
            except EOFError:
                break       

if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    # save it to a file
    # logger.info("loading frames")
    # save_frames('./samples/video_1.mp4','./frames.pkl')
    # save_frames('./samples/Segment_00000.mov','./frames.mov.pkl')
    # detect players
    logger.info("using frames to generate tracks")
    frames = get_frames('./frames.mov.pkl')
    # stream_processing('./frames.mov.pkl','tracks.pkl')
    logger.info("complete... now using tracks to get players")

    tracks = get_frames('./tracks.pkl')
    player_ids = []
    for track in tracks:
        for key in track:
            if key not in player_ids:
                player_ids.append(key)
    # # tracks = detect_players(frames)
    # have a bunch of players, now lets get their touches
    # player_assignments = []
    # player_assignments = get_team_assignment(frames,tracks,"white shirt","dark blue shirt")
    # # save the player assignments
    # with open('./teams.pkl','wb') as f:
    #     pickle.dump(player_assignments,f)
    # we now have
    # - frames in a pkl
    # - players and their tracks in a pkl
    # - player-to-team in a pkl
    # let's do some ball work
    logger.info("starting to process ball positions")
    # process_frames_for_ball_stream('./frames.mov.pkl','./balls.pkl')
    logger.info("complete")
    
    

