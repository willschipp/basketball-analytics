from detectors import TeamAssigner, CourtKeypointDetector, PassAndInterceptionDetector, BallAquisitionDetector, TacticalViewConverter
from trackers import BallTracker, PlayerTracker, SpeedAndDistanceCalculator
from utils import read_video

import os

PLAYER_DETECTOR_PATH = "models/player_detector.pt"
BALL_DETECTOR_PATH = "models/ball_detector_model.pt"
COURT_KEYPOINT_DETECTOR_PATH = "models/court_keypoint_detector.pt"

def main(video_location,stub_path):
    # upload the video and run the detector
    video_frames = read_video(video_location)

    # setup the trackers
    player_tracker = PlayerTracker(PLAYER_DETECTOR_PATH)
    ball_tracker = BallTracker(BALL_DETECTOR_PATH)
    court_tracker = CourtKeypointDetector(COURT_KEYPOINT_DETECTOR_PATH)

    # run the detectors
    player_tracks = player_tracker.get_object_tracks(video_frames,read_from_stub=True,stub_path=os.path.join(stub_path,'player_Track_stubs.pkl'))

    # dump
    # print(player_tracks)

    # team assigner
    team_assigner = TeamAssigner()
    player_assignment = team_assigner.get_player_teams_across_frames(video_frames,player_tracks,read_from_stub=True,stub_path=os.path.join(stub_path,'player_Track_stubs.pkl'))

    # ball tracks
    ball_tracks = ball_tracker.get_object_tracks(video_frames,read_from_stub=True,stub_path=os.path.join(stub_path, 'ball_track_stubs.pkl'))                                             

    # clean up
    ball_tracks = ball_tracker.remove_wrong_detections(ball_tracks)
    # refine
    ball_tracks = ball_tracker.interpolate_ball_positions(ball_tracks)

    # Ball Acquisition
    ball_aquisition_detector = BallAquisitionDetector()
    ball_aquisition = ball_aquisition_detector.detect_ball_possession(player_tracks,ball_tracks)

    # Detect Passes
    pass_and_interception_detector = PassAndInterceptionDetector()
    passes = pass_and_interception_detector.detect_passes(ball_aquisition,player_assignment)
    interceptions = pass_and_interception_detector.detect_interceptions(ball_aquisition,player_assignment)

    # Tactical View
    tactical_view_converter = TacticalViewConverter(
        court_image_path="./images/basketball_court.png"
    )

    # key  points
    court_keypoints_per_frame = court_tracker.get_court_keypoints(video_frames,read_from_stub=True,stub_path=os.path.join(stub_path, 'court_key_points_stub.pkl'))
    court_keypoints_per_frame = tactical_view_converter.validate_keypoints(court_keypoints_per_frame)
    tactical_player_positions = tactical_view_converter.transform_players_to_tactical_view(court_keypoints_per_frame,player_tracks)

    # Speed and Distance Calculator
    speed_and_distance_calculator = SpeedAndDistanceCalculator(
        tactical_view_converter.width,
        tactical_view_converter.height,
        tactical_view_converter.actual_width_in_meters,
        tactical_view_converter.actual_height_in_meters
    )
    player_distances_per_frame = speed_and_distance_calculator.calculate_distance(tactical_player_positions)
    player_speed_per_frame = speed_and_distance_calculator.calculate_speed(player_distances_per_frame)


    # build an object that contains player id and number of touches
    player_ids = []
    track_counter = 0
    for track in player_tracks:
        obj_counter = 0
        for obj in track:            
            # structure is frame number, track_id/player_id = bounding box (4 coords)
            # print(f"track {track_counter} obj {obj_counter} val {obj} track_obj {track[obj]}")
            # obj represents the player id
            obj_counter += 1
            if obj not in player_ids:
                player_ids.append(obj) # add to the player set
        track_counter += 1

    # for player_id in player_ids:
    #     print(player_id)
    
    touches = [{
        "player_id":None,
        "touches":0
    }]

    # for ball_track in ball_tracks:
    #     print(f" ball track {ball_track}")

    # get ball touches
    # for ball_touch in ball_aquisition:
    #     print(f"{ball_touch} {ball_aquisition[ball_touch]}")

    print(touches)


if __name__ == "__main__":
    main("./samples/video_1.mp4","./stubs")

