import cv2
import os
import pickle

def save_frames(video_path,frames_name):
    batch_size = 20 # TODO allow overrides
    frames = []
    cap = cv2.VideoCapture(video_path)
    frame_num = 0
    with open(frames_name,'wb') as f:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
            if len(frames) == batch_size:
                # write it out
                pickle.dump(frames,f)
                frames = [] #reset
        if frames:
            # dump the last of it
            pickle.dump(frames,f)
    cap.release()
    

def get_frames(pkl_path):
    frames = []
    with open(pkl_path,'rb') as f:
        frames = pickle.load(f)    
    return frames