from ultralytics import YOLO
import supervision as sv

def detect_players(frames,limit=-1):
    model = YOLO('models/player_detector.pt')
    frame_counter = 0
    for idx, frame in enumerate(frames):
        # results = model(frame)
        results = model.predict(frame,conf=0.5) #50% confidence
        cls_names = results[0].names
        cls_names_inv = {v:k for k,v in cls_names.items()}
        # convert 
        supervised = sv.Detections.from_ultralytics(results[0])
        # try with tracks
        for sup in supervised:
            print(f" {sup[3]}")
        # for cls in results[0].boxes.cls:
        #     print(f"cls {cls}")
        # print(f"result {results[0].boxes.cls[0]}")
        if limit > -1:
            if frame_counter >= limit:
                break
        frame_counter += 1
    
