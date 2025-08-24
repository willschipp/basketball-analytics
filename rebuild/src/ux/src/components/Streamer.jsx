

function Streamer() {

    // peer connection
    var pc = null;

    // data channel
    var dc = null, dcInterval = null;

    function createPeerConnection() {
        var config = {
            sdpSemantics: 'unified-plan'
        };

        pc = new RTCPeerConnection(config);

        // register some listeners to help debugging
        pc.addEventListener('icegatheringstatechange', () => {
            console.log("icegatheringstatechange " + pc.iceGatheringState);
        }, false);

        pc.addEventListener('iceconnectionstatechange', () => {
            console.log("iceconnectionstatechange " + pc.iceGatheringState);
        }, false);
        
        pc.addEventListener('signalingstatechange', () => {
            console.log("signalingstatechange " + pc.signalingState);
        }, false);
        
        // connect audio / video
        pc.addEventListener('track', (evt) => {
            if (evt.track.kind == 'video')
                document.getElementById('video').srcObject = evt.streams[0];
            else
                document.getElementById('audio').srcObject = evt.streams[0];
        });

        return pc;
    }

    function negotiate() {
        return pc.createOffer().then((offer) => {
            return pc.setLocalDescription(offer);
        }).then(() => {
            // wait for ICE gathering to complete
            return new Promise((resolve) => {
                if (pc.iceGatheringState === 'complete') {
                    resolve();
                } else {
                    function checkState() {
                        if (pc.iceGatheringState === 'complete') {
                            pc.removeEventListener('icegatheringstatechange', checkState);
                            resolve();
                        }
                    }
                    pc.addEventListener('icegatheringstatechange', checkState);
                }
            });
        }).then(() => {
            var offer = pc.localDescription;

            var video_id = crypto.randomUUID();

            return fetch('/offer', {
                body: JSON.stringify({
                    sdp: offer.sdp,
                    type: offer.type,
                    video_transform: "",
                    video_id: video_id
                }),
                headers: {
                    'Content-Type': 'application/json'
                },
                method: 'POST'
            });
        }).then((response) => {
            return response.json();
        }).then((answer) => {
            console.log(answer.sdp);
            return pc.setRemoteDescription(answer);
        }).catch((e) => {
            alert(e);
        });
    }

    function start() {
        document.getElementById('start').style.display = 'none';

        pc = createPeerConnection();

        var time_start = null;

        const current_stamp = () => {
            if (time_start === null) {
                time_start = new Date().getTime();
                return 0;
            } else {
                return new Date().getTime() - time_start;
            }
        };

        var parameters = JSON.parse('{"ordered": true}');

        dc = pc.createDataChannel('chat', parameters);
        dc.addEventListener('close', () => {
            clearInterval(dcInterval);
            // dataChannelLog.textContent += '- close\n';
            console.log('dataChannelLog ' + '- close');
        });
        dc.addEventListener('open', () => {
            console.log('dataChannelLog ' + '- open');
            dcInterval = setInterval(() => {
                var message = 'ping ' + current_stamp();
                console.log('dataChannelLog ' + '> ' + message);
                dc.send(message);
            }, 1000);
        });
        dc.addEventListener('message', (evt) => {
            console.log('dataChannelLog ' + '< ' + evt.data);

            if (evt.data.substring(0, 4) === 'pong') {
                var elapsed_ms = current_stamp() - parseInt(evt.data.substring(5), 10);
                console.log('dataChannelLog ' + ' RTT ' + elapsed_ms + 'ms');
            }
        });
        // }

        // Build media constraints.

        const constraints = {
            audio: false,
            video: false
        };

        const audioConstraints = {};

        constraints.audio = Object.keys(audioConstraints).length ? audioConstraints : true;

        const videoConstraints = {};

        constraints.video = Object.keys(videoConstraints).length ? videoConstraints : true;
        // }

        // Acquire media and start negociation.

        if (constraints.audio || constraints.video) {
            // if (constraints.video) {
            //     document.getElementById('media').style.display = 'block';
            // }
            navigator.mediaDevices.getUserMedia(constraints).then((stream) => {
                stream.getTracks().forEach((track) => {
                    pc.addTrack(track, stream);
                });
                return negotiate();
            }, (err) => {
                alert('Could not acquire media: ' + err);
            });
        } else {
            negotiate();
        }

        document.getElementById('stop').style.display = 'inline-block';
    }

    function stop() {
        document.getElementById('stop').style.display = 'none';
        document.getElementById('start').style.display = 'inline-block'; //re-expose

        // close data channel
        if (dc) {
            dc.close();
        }

        // close transceivers
        if (pc.getTransceivers) {
            pc.getTransceivers().forEach((transceiver) => {
                if (transceiver.stop) {
                    transceiver.stop();
                }
            });
        }

        // close local audio / video
        pc.getSenders().forEach((sender) => {
            sender.track.stop();
        });

        // close peer connection
        setTimeout(() => {
            pc.close();
        }, 500);
    }

    return (
        <>
            <h4>Stream</h4>
            <button id="start" className="btn btn-sm btn-outline-secondary" onClick={start}>Start</button>
            <button id="stop" className="btn btn-sm btn-outline-secondary" style={{display: "none"}} onClick={stop}>Stop</button>

            <audio id="audio"></audio>
            <video id="video" playsInline={true}></video>
        </>
    );
}

export default Streamer