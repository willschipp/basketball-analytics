from utils.frame_tools import save_frames,get_frames
from detector.players import detect_players

if __name__ == "__main__":
    # save it to a file
    print("loading frames")
    # save_frames('./samples/video_1.mp4','./frames.pkl')
    # detect players
    print("using frames")
    frames = get_frames('./frames.pkl')
    detect_players(frames,10)

