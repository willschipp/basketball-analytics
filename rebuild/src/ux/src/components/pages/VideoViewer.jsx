
import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';

function VideoViewer() {
    const location = useLocation();
    const { videoId } = location.state || {};
    const [ gameTitle,setGameTitle ] = useState("");
    const [ timestamp,setTimestamp ] = useState("");
    const [ url, setUrl ] = useState("")

    const loadVideo = (videoId) => {
        fetch(`/api/v1/videos/${videoId}`)
        .then(response => response.json())
        .then(data => {
            setGameTitle(data.title);
            setTimestamp(data.timestamp);
            let url = `/api/v1/videos/${videoId}/stream`;
            setUrl(url)

            console.log(data);
            console.log(url);
        });
    }

    useEffect(() => {
        if (videoId) {
            //load the video
            loadVideo(videoId);
        }
    },[]);

    return (
        <>
            <div className="container-fluid d-flex justify-content-center align-items-center h-100 w-100 bg-white text-primary-dark" style={{ color: "#162948" }}>
                <div className="row w-100 h-100 mt-4">
                    <div className="col-md-9 d-flex flex-column gap-3">
                        <div className="card p-3 text-center">
                            { (url) ? (
                                <video controls muted playsInline autoPlay={true} width="100%" style={{ maxHeight: "400px" }}>
                                    <source src={url} type={url.endsWith(".mp4") ? "video/mp4" : "video/quicktime"} />
                                    Your browser does not support the video tag.
                                </video>
                            ) : (
                                <>
                                    <h5>Video Not Found</h5>
                                </>
                            )}
                        </div>
                    </div>
                    <div className="col-md-3 d-flex flex-column">
                        <div className="card p-3 text-center">
                            <h5>Game ({(gameTitle) ? (<>{gameTitle}</>) : (<>not found</>)})</h5>
                            <p>{(timestamp) ? (<>{timestamp}</>) : (<>-</>)}</p>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}

export default VideoViewer