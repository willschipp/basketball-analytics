from ultralytics import YOLO
import supervision as sv

import logging
import os
import psutil

logger = logging.getLogger(__name__)

def detect_players(frames):
    process = psutil.Process(os.getpid())
    ram_used = process.memory_info().rss / (1024 * 1024)     
    logger.info(f"RAM used before model load {round(ram_used, 2)} MB")

    model = YOLO('models/player_detector.pt')
    tracker = sv.ByteTrack()
    frame_counter = 0

    ram_used = process.memory_info().rss / (1024 * 1024)     
    logger.info(f"RAM used after model load  {round(ram_used, 2)} MB")

    logger.info("starting detections")

    batch_size=20 
    detections = [] 
    for i in range(0,len(frames),batch_size):
        detections_batch = model.predict(frames[i:i+batch_size],conf=0.5)
        detections += detections_batch

    logger.info("detections complete")

    tracks = []

    # for idx, frame in enumerate(frames):
    for idx, frame in enumerate(detections):
        class_names = frame.names
        class_names_inverted = {v:k for k,v in class_names.items()}
        # print("now supervised...")
        supervised = sv.Detections.from_ultralytics(frame)
        # get tracks
        detection_with_tracks = tracker.update_with_detections(supervised)

        tracks.append({})
        

        for frame_detection in detection_with_tracks:            
            #bounding box
            bbox = frame_detection[0].tolist()
            #detected id
            class_id = frame_detection[3]
            track_id = frame_detection[4]
            # validate that this is tracking a PLAYER
            if class_id == class_names_inverted['Player']:
                tracks[idx][track_id] = bbox
    
    logger.info("done... returning")

    return tracks

    
