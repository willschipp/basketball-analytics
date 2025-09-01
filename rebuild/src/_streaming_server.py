import argparse
import asyncio
import json
import logging
import os
import ssl
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

# SSL config
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile='./certs/selfsigned.crt', keyfile='./certs/selfsigned.key')


class VideoTransformTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, track, transform):
        super().__init__()  # don't forget this!
        self.track = track
        self.transform = transform

    async def recv(self):
        frame = await self.track.recv()

        # extract the frame to send for processing
        # img = frame.to_ndarray(format="bgr24")

        return frame # without transformations



# define endpoints
async def index(request):
    content = open(os.path.join(ROOT, "client/index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)

# client endpoint
async def javascript(request):
    content = open(os.path.join(ROOT, "client/static/client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)


async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    pcs.add(pc)

    def log_info(msg, *args):
        logger.info(pc_id + " " + msg, *args)

    log_info("Created for %s", request.remote)

    recordings_dir = "./recordings"
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="WebRTC audio / video / data-channels demo"
    )
    parser.add_argument("--cert-file", help="SSL certificate file (for HTTPS)")
    parser.add_argument("--key-file", help="SSL key file (for HTTPS)")
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host for HTTP server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for HTTP server (default: 8080)"
    )
    parser.add_argument("--record-to", help="Write received media to a file.")
    parser.add_argument("--verbose", "-v", action="count")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # if args.cert_file:
    # ssl_context = ssl.SSLContext()
    # ssl_context.load_cert_chain(args.cert_file, args.key_file)
    # else:
    #     ssl_context = None

    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/static/client.js", javascript)
    app.router.add_post("/offer", offer)
    # app, access_log=None, host=args.host, port=args.port, ssl_context=ssl_context
    web.run_app(
        app, access_log=None, host="0.0.0.0", port=8443, ssl_context=ssl_context
    )