import cv2
import os
import pickle

def save_frames(video_path,frames_name):
    frames = []
    cap = cv2.VideoCapture(video_path)
    frame_num = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
        frame_num += 1
    # dump to pkl
    with open(frames_name,'wb') as f:
        pickle.dump(frames,f)
    

def get_frames(pkl_path):
    frames = []
    with open(pkl_path,'rb') as f:
        frames = pickle.load(f)    
    return frames