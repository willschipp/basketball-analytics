FROM python:3.12-slim AS build

# update for dependencies
# RUN apt-get update && apt-get install -y libgl1 libglib2.0-0
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 wget && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /usr/local/app

# Copy only requirements first for better build caching
COPY requirements.txt ./

# Install dependencies
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY src ./src

RUN mkdir -p ./src/models && \
    wget -O ./src/models/ball_detector_model.pt https://storage.googleapis.com/basketball_model_bucket/yolo_models/ball_detector_model.pt && \
    wget -O ./src/models/player_detector.pt https://storage.googleapis.com/basketball_model_bucket/yolo_models/player_detector.pt && \
    wget -O ./src/models/patrickjohncyh/fashion-clip/model.safetensors https://storage.googleapis.com/basketball_model_bucket/patrickjohncyh/fashion-clip/model.safetensors

FROM python:3.12-slim AS run

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/local/app

COPY --from=build /install /usr/local

COPY --from=build /usr/local/app/src ./src

# Use a non-root user for security
RUN useradd --create-home app

# own the directory
RUN chown -R app:app /usr/local/app /tmp

# Expose a port (change 5000 to your app's port)
EXPOSE 5000

# switch user
USER app

# Default command to run your app (adjust as needed)
CMD ["python", "./src/main.py"]