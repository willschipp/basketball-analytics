# Models

## Where are they?

- models are not persisted in git but in a cloud S3 storage
- model files are best retrieved using
```sh
wget -O ./ball_detector_model.pt https://storage.googleapis.com/basketball_model_bucket/yolo_models/ball_detector_model.pt
wget -O ./player_detector.pt https://storage.googleapis.com/basketball_model_bucket/yolo_models/player_detector.pt
wget -O ./patrickjohncyh/fashion-clip/model.safetensors https://storage.googleapis.com/basketball_model_bucket/patrickjohncyh/fashion-clip/model.safetensors
```

