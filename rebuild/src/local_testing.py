from service.processor import process_frames_for_ball_stream
from utils.file_tools import get_list
from utils.frame_tools import write_frame

import cv2
import pickle

def images():
    # load up the frames pickle
    # pick one and dump it out
    # see if it comes to an image
    frames = get_list('./frames.pkl')    
    tracks = get_list('./tracks.pkl')
    print(f"frames {len(frames)} tracks {len(tracks)}")
    # write_frame(frames[0],"./frame_0.jpg")
    frame = frames[0]
    for idx,track in enumerate(tracks):
        for player_id,player_info in track.items():
            print(f"player_id {player_id} player_info {player_info}")
            # for each, draw a bounding box on this single frame
            # start_point = (int(player_info[0]),int(player_info[1]))
            # end_point = (int(player_info[2]),int(player_info[3]))
            # color = (0,255,0) # green
            # thickness = 2 #2px
            x_min, y_min, x_max, y_max = map(int, player_info)
            cropped_frame = frame[y_min:y_max, x_min:x_max]
            cv2.imwrite(f"players/frame_{idx}_player_{player_id}_crop.jpg",cropped_frame)
        # cv2.rectangle(frame,start_point,end_point,color,thickness)
    #write the image
    # write_frame(frame,"./frame_0.jpg")


def build_player_model():
    # goal is to build a player model
    # now we have a full list of;
    # players
    # team mappings
    # passes
    # interceptions
    # possessions
    # and they're mapped to frames
    # now build a grid which shows the following
    # | team | player | passes | intercepts |
    # |------|--------|--------|------------|
    # | a    | 1      |   10   |    0       |
    # | a    | 2      |   3    |    4       |
    # |______|________|________|____________|
    # 
    # tracks has player ids and bounding boxes for each FRAME
    # iterate over tracks to player_id and player info in each frame
    # 
    #     
    tracks = get_list('./tracks.pkl')
    teams = get_list('./teams.pkl')
    players = []
    player_ids = set()
    for idx,team in enumerate(teams):
        for player_id,team_id in team.items():
            if player_id not in player_ids:
                player = {
                    'player_id':int(player_id),
                    'team_id':team_id
                }
                players.append(player)
                player_ids.add(player_id)
    # now we have a set of unique players
    print(players)
    # for each player, pull their image from the respective tracks
    # do so by looping over the frames, and then pulling the crops


def fix_ball():
    process_frames_for_ball_stream('./frames.pkl','./ball.pkl')
    



if __name__ == "__main__":
    # images()
    # build_player_model()
    fix_ball()