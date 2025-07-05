from ultralytics import YOLO
import supervision as sv

import logging
import os
import psutil

logger = logging.getLogger(__name__)

def detect_ball(frames):
    process = psutil.Process(os.getpid())
    ram_used = process.memory_info().rss / (1024 * 1024)     
    logger.info(f"RAM used before model load {round(ram_used, 2)} MB")
    # setup
    model = YOLO('models/player_detector.pt')

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

    return tracks