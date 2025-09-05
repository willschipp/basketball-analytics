import argparse
import asyncio
from datetime import datetime
import json
import logging
import os
import uuid

import cv2
from aiohttp import web
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, MediaRelay
from av import VideoFrame

ROOT = os.path.dirname(__file__)

logger = logging.getLogger("pc")
pcs = set()
relay = MediaRelay()


class VideoTransformTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, track, transform):
        super().__init__()  # don't forget this!
        self.track = track
        self.transform = transform

    async def recv(self):
        frame = await self.track.recv()

        return frame # without transformations


async def offer(request):
    params = await request.json()

    # get the database and save it
    video_id = params['video_id']    
    # create the video object and save
    video = {
        "id": video_id,
        "title": "",
        "timestamp": datetime.now().isoformat(),
        "url": f"{video_id}.mp4",
        "fileType":".mp4"
    }
    # save
    db = request.app["dbm"]
    video_json = json.dumps(video)
    await db.set(video_id,video_json) # wait for it to write
    logger.info(f"have written {video_id} to the database file as a {video_json}")

    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    pcs.add(pc)

    def log_info(msg, *args):
        logger.info(pc_id + " " + msg, *args)

    log_info("Created for %s", request.remote)

    recordings_dir = "./data" #changed directory
    os.makedirs(recordings_dir, exist_ok=True)

    output_location = os.path.join(recordings_dir, f"{params['video_id']}.mp4")
    # if args.record_to:
    recorder = MediaRecorder(output_location)
    # else:
        # recorder = MediaBlackhole()

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:])

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log_info("Connection state is %s", pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)

        if track.kind == "audio":
            # pc.addTrack(player.audio)
            recorder.addTrack(track)
        elif track.kind == "video":
            transformed_track = VideoTransformTrack(
                relay.subscribe(track), transform=params.get("video_transform")
            )
            pc.addTrack(transformed_track)  # add transformed track to pc
            recorder.addTrack(transformed_track)  # record the transformed track only

        @track.on("ended")
        async def on_ended():
            log_info("Track %s ended", track.kind)
            try:
                await asyncio.sleep(0.1)  # small delay to allow packets to flush
                await recorder.stop()
                log_info("Recorder stopped cleanly")
                # send the video for parsing
            except Exception as e:
                logger.error("Exception during recorder.stop(): %s", e)

    # handle offer
    await pc.setRemoteDescription(offer)
    await recorder.start()

    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

def create_stream_server(shared_dbm):
    app = web.Application()
    # add the database
    app['dbm'] = shared_dbm
    # add the routes and hooks
    app.on_shutdown.append(on_shutdown)
    app.router.add_post("/offer", offer)
    return app