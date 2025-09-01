import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import '../styles/Videos.css';

import UploadForm from '../form/UploadForm';

const VIDEO_URL = '/api/v1/videos';


function formatDate(dateString) {
    const date = new Date(dateString);
    const day = date.getDate().toString().padStart(2, '0');
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const month = monthNames[date.getMonth()];
    const year = date.getFullYear().toString().slice(-2);
    return `${day} ${month} ${year}`;
}

function Videos() {

    const [videos, setVideos] = useState([]);
    const [loading, setLoading] = useState(true); //loading because it's an onload scenario

    const navigate = useNavigate();

    const loadVideos = () => {
        fetch(VIDEO_URL)
            .then((res) => res.json())
            .then((data) => {
                setVideos(data);
                setLoading(false);
            });
    }

    useEffect(() => {
        loadVideos();
    },[]);

    const handleNavigateVideo = (videoId) => {
        //pass the location
        navigate('/videos/viewer', {state: { videoId: videoId }});
    }

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <> 
            <div className="container-fluid d-flex justify-content-center align-items-center h-100 w-100 bg-white text-primary-dark" style={{ color: "#162948" }}>
                <div className="row w-100 h-100 mt-4">
                    <div className="col-md-6 d-flex flex-column gap-3">
                        {videos.map((video) => (
                            <div key={video.id} className="card p-3 text-center">
                                <a href="#" onClick={(e) => {e.preventDefault(); handleNavigateVideo(video.id)}}>{formatDate(video.timestamp)}</a>
                            </div>
                        ))}
                    </div>
                    <div className="col-md-6 d-flex flex-column gap-3">
                        <UploadForm refreshFunction={loadVideos}/>
                    </div>
                </div>
            </div>
        </>
    );
}

export default Videos