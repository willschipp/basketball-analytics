from PIL import Image
import cv2
from transformers import CLIPProcessor, CLIPModel

import logging

logger = logging.getLogger(__name__)

team_colors = {}
player_team_dict = {}

model = CLIPModel.from_pretrained("patrickjohncyh/fashion-clip")
processor = CLIPProcessor.from_pretrained("patrickjohncyh/fashion-clip")


def get_player_color(frame,bbox,team_1_class_name,team_2_class_name):
    image = frame[int(bbox[1]):int(bbox[3]),int(bbox[0]):int(bbox[2])]

    # Convert to PIL Image
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_image)
    image = pil_image

    classes = [team_1_class_name, team_2_class_name]

    inputs = processor(text=classes, images=image, return_tensors="pt", padding=True)

    outputs = model(**inputs)
    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1)   

    class_name = classes[probs.argmax(dim=1)[0]]

    return class_name      


def get_player_team(frame,player_bbox,player_id,team_1_class_name,team_2_class_name):
    global player_team_dict
    # check
    if player_id in player_team_dict:
        return player_team_dict[player_id]

    player_color = get_player_color(frame,player_bbox,team_1_class_name,team_2_class_name)

    team_id=2
    if player_color==team_1_class_name:
        team_id=1

    player_team_dict[player_id] = team_id
    return team_id


def get_team_assignment(frames,player_tracks,team_1_class_name,team_2_class_name):
    global player_team_dict
    # load the model

    player_assignment = []
    for frame_num, player_track in enumerate(player_tracks):
        player_assignment.append({})

        if frame_num %50 == 0:
            player_team_dict = {}
        
        for player_id, track in player_track.items():
            team = get_player_team(frames[frame_num],track,player_id,team_1_class_name,team_2_class_name)
            player_assignment[frame_num][player_id] = team

    return player_assignment

