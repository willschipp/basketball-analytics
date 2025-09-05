import sportslabkit as slk

# Initialize your camera and models
cam = slk.Camera('./samples/video_1.mp4')
det_model = slk.detection_model.load('YOLOv8x')
motion_model = slk.motion_model.load('KalmanFilter')

# Configure and execute the tracker
tracker = slk.mot.SORTTracker(detection_model=det_model, motion_model=motion_model)
bbdf = tracker.track(cam)

print("done... let's look")

print(bbdf)