from ultralytics import YOLO
import supervision as sv

import gc
import logging
import numpy as np
import os
import pandas as pd
import psutil
import torch

from utils.detector_utils import get_center_of_bbox, measure_distance

logger = logging.getLogger(__name__)

# set global configurables
possession_threshold = 50
min_frames = 5
containment_threshold = 0.8

def detect_ball(frames,use_gpu=True):
    process = psutil.Process(os.getpid())
    ram_used = process.memory_info().rss / (1024 * 1024)     
    logger.info(f"RAM used before model load {round(ram_used, 2)} MB")
    # setup
    device = 'cuda' if use_gpu and torch.cuda.is_available() else 'cpu'

    runtime_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(runtime_dir, '..', 'models', 'ball_detector_model.pt')

    model = YOLO(model_path)
    model.to(device)

    ram_used = process.memory_info().rss / (1024 * 1024)     
    logger.info(f"RAM used after model load  {round(ram_used, 2)} MB")

    logger.info("starting ball detections")
    # detect
    batch_size=20 
    detections = [] 
    for i in range(0,len(frames),batch_size):
        detections_batch = model.predict(frames[i:i+batch_size],conf=0.5)
        detections += detections_batch

    tracks=[]

    for idx, frame in enumerate(detections):
        class_names = frame.names
        class_names_inverted = {v:k for k,v in class_names.items()}

        # Covert to supervision Detection format
        detection_supervision = sv.Detections.from_ultralytics(frame)

        tracks.append({})
        chosen_bbox =None
        max_confidence = 0
        
        for frame_detection in detection_supervision:
            bbox = frame_detection[0].tolist()
            cls_id = frame_detection[3]
            confidence = frame_detection[2]
            
            if cls_id == class_names_inverted['Ball']:
                if max_confidence<confidence:
                    chosen_bbox = bbox
                    max_confidence = confidence

        if chosen_bbox is not None:
            tracks[idx][1] = {"bbox":chosen_bbox}
    
    logger.info("done... returning")

    # unload the model
    gc.collect()

    ram_used = process.memory_info().rss / (1024 * 1024)
    logger.info(f"RAM used after model unloaded  {round(ram_used, 2)} MB")
    # return
    return tracks

def remove_wrong_detections(ball_tracks):
    # set tolerances
    maximum_allowed_distance = 25
    last_good_frame_index = -1

    for i in range(len(ball_tracks)):
        current_box = ball_tracks[i].get(1,{}).get('bbox',[])
        if len(current_box) == 0:
            continue
        
        if last_good_frame_index == -1:
            last_good_frame_index = i
            continue

        last_good_box = ball_tracks[last_good_frame_index].get(1,{}).get('bbox',[])
        frame_gap = i - last_good_frame_index
        adjusted_max_distance = maximum_allowed_distance * frame_gap # figure out the max distaance allowed

        if np.linalg.norm(np.array(last_good_box[:2]) - np.array(current_box[:2])) > adjusted_max_distance: #linear algorithm for distance
            ball_tracks[i] = {}
        else:
            last_good_frame_index = i

    return ball_tracks

def refine(ball_tracks):
    ball_tracks = [x.get(1,{}).get('bbox',[]) for x in ball_tracks]
    df_ball_positions = pd.DataFrame(ball_tracks,columns=['x1','y1','x2','y2'])
    #get missing values
    df_ball_positions = df_ball_positions.interpolate()
    df_ball_positions = df_ball_positions.bfill()
    #reset
    ball_tracks = [{1: {'bbox':x}} for x in df_ball_positions.to_numpy().tolist()]
    return ball_tracks

# calculate how close the ball is the to the players box
def calculate_ball_containment_ratio(player_bbox,ball_bbox):
    px1, py1, px2, py2 = player_bbox
    bx1, by1, bx2, by2 = ball_bbox
    
    intersection_x1 = max(px1, bx1)
    intersection_y1 = max(py1, by1)
    intersection_x2 = min(px2, bx2)
    intersection_y2 = min(py2, by2)
    
    if intersection_x2 < intersection_x1 or intersection_y2 < intersection_y1:
        return 0.0
        
    intersection_area = (intersection_x2 - intersection_x1) * (intersection_y2 - intersection_y1)
    ball_area = (bx2 - bx1) * (by2 - by1)
    
    return intersection_area / ball_area    

# get the points used for assignment
def get_key_basketball_player_assignment_points(player_bbox,ball_center):
    ball_center_x = ball_center[0]
    ball_center_y = ball_center[1]

    x1, y1, x2, y2 = player_bbox
    width = x2 - x1
    height = y2 - y1

    output_points = []    
    if ball_center_y > y1 and ball_center_y < y2:
        output_points.append((x1, ball_center_y))
        output_points.append((x2, ball_center_y))

    if ball_center_x > x1 and ball_center_x < x2:
        output_points.append((ball_center_x, y1))
        output_points.append((ball_center_x, y2))

    output_points += [
        (x1 + width//2, y1),          # top center
        (x2, y1),                      # top right
        (x1, y1),                      # top left
        (x2, y1 + height//2),          # center right
        (x1, y1 + height//2),          # center left
        (x1 + width//2, y1 + height//2), # center point
        (x2, y2),                      # bottom right
        (x1, y2),                      # bottom left
        (x1 + width//2, y2),          # bottom center
        (x1 + width//2, y1 + height//3), # mid-top center
    ]
    return output_points

# calculate the minimum distance
def find_minimum_distance_to_ball(ball_center,player_bbox):
    key_points = get_key_basketball_player_assignment_points(player_bbox,ball_center)
    return min(measure_distance(ball_center, point) for point in key_points)    

# function to check which is the best possession candidate in a given frame
def find_best_candidate_for_possession(ball_center,player_frame,ball_bbox):
    # init
    high_containment_players = []
    regular_distance_players = []
    # loop
    for player_id, player_info in player_frame.items():        
        if not player_info:
            continue
            
        containment = calculate_ball_containment_ratio(player_info, ball_bbox)
        min_distance = find_minimum_distance_to_ball(ball_center, player_info)

        if containment > containment_threshold:
            high_containment_players.append((player_id, min_distance))
        else:
            regular_distance_players.append((player_id, min_distance))

    # First priority: players with high containment
    if high_containment_players:
        best_candidate = max(high_containment_players, key=lambda x: x[1])
        return best_candidate[0]
        
    # Second priority: players within distance threshold
    if regular_distance_players:
        best_candidate = min(regular_distance_players, key=lambda x: x[1])
        if best_candidate[1] < possession_threshold:
            return best_candidate[0]
                
    return -1    

def detect_possession(player_tracks,ball_tracks):
    # init
    global min_frames #TODO remove global
    num_frames = len(ball_tracks)
    position_list = [-1] * num_frames #create list
    consecutive_possession_count = {}

    for frame_num in range(num_frames):
        ball_info = ball_tracks[frame_num].get(1,{})
        if not ball_info:
            continue
        
        ball_bbox = ball_info.get('bbox',[])
        if not ball_bbox:
            continue

        ball_center = get_center_of_bbox(ball_bbox)


        best_player_id = find_best_candidate_for_possession(ball_center,player_tracks[frame_num],ball_bbox)

        if best_player_id != -1:
            # got a hit --> update the count
            number_of_consecutive_frames = consecutive_possession_count.get(best_player_id,0) + 1
            consecutive_possession_count = {best_player_id: number_of_consecutive_frames}

            if consecutive_possession_count[best_player_id] >= min_frames:
                logger.info("greater than min frames")
                position_list[frame_num] = best_player_id
        else:
            consecutive_possession_count = {}
    
    return position_list # final list

def detect_passes(possession_list,teams_list):
    passes = [-1] * len(possession_list)
    prev_holder = -1
    previous_frame = -1

    for frame in range(1,len(possession_list)):
        if possession_list[frame -1] != -1:
            prev_holder = possession_list[frame - 1]
            previous_frame = frame -1
        
        current_holder = possession_list[frame]

        if prev_holder != -1 and current_holder != -1 and prev_holder != current_holder:
            prev_team = teams_list[previous_frame].get(prev_holder, -1)
            current_team = teams_list[frame].get(current_holder,-1)

            if prev_team == current_team and prev_team != -1:
                passes[frame] = prev_team
    
    return passes

def detect_interceptions(possession_list,teams_list):
    interceptions = [-1] * len(possession_list)
    prev_holder = -1
    previous_frame = -1

    for frame in range(1,len(possession_list)):
        if possession_list[frame -1] != -1:
            prev_holder = possession_list[frame - 1]
            previous_frame = frame -1
        
        current_holder = possession_list[frame]

        if prev_holder != -1 and current_holder != -1 and prev_holder != current_holder:
            prev_team = teams_list[previous_frame].get(prev_holder, -1)
            current_team = teams_list[frame].get(current_holder,-1)

            if prev_team != current_team and prev_team != -1 and current_team != -1:
                interceptions[frame] = prev_team
    
    return interceptions
