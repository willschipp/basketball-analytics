import cv2
from ultralytics import YOLO
import os

# load up the model
# model = YOLO('models/yolo12n.pt')
model = YOLO('models/ball_detector_model.pt')

# split the video up into frames
video_path = 'samples/video_1.mp4'
frame_target = "frames"
os.makedirs(frame_target, exist_ok=True)
cap = cv2.VideoCapture(video_path)
frame_num = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_filename = os.path.join(frame_target, f"frame_{frame_num:05d}.jpg")
    cv2.imwrite(frame_filename, frame)
    frame_num += 1

cap.release()
# cv2.destroyAllWindows()

frame_counter = 0

# now lets look at the frames
frame_files = sorted([f for f in os.listdir(frame_target) if f.lower().endswith(('.jpg'))])
for fname in frame_files:
    frame_path = os.path.join(frame_target, fname)
    frame = cv2.imread(frame_path)
    if frame is None:
        continue
    
    # Run detection
    results = model(frame)
    
    print(f" frame {fname} results {results[0].boxes.cls[0]}")
    frame_counter += 1

    if frame_counter >= 10:
        break

    # # Draw detections
    # for box in results[0].boxes:
    #     cls_id = int(box.cls[0])
    #     conf = float(box.conf[0])
    #     x1, y1, x2, y2 = map(int, box.xyxy[0])
        
    #     # Assuming basketball is class 0; adjust as needed
    #     if cls_id == 0 and conf > conf_threshold:
    #         cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    #         cv2.putText(frame, f'Basketball: {conf:.2f}', (x1, y1-10),
    #                     cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    #         print(f"Detected basketball in {fname} with confidence {conf:.2f}")

