import React, { useState, useEffect } from 'react';

import '../styles/Videos.css';

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

    useEffect(() => {
        fetch(VIDEO_URL)
            .then((res) => res.json())
            .then((data) => {
                setVideos(data);
                setLoading(false);
            });
    },[]);

    const handleNavigateVideo = (videoId) => {
        console.log(videoId);
    }

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <> 
            <table className="table">
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Title</th>
                    </tr>
                </thead>
                <tbody>
                    {videos.map((video) => (
                        <tr key={video.id}>
                            <td>
                                <a href="#" onClick={(e) => {
                                        e.preventDefault();
                                        handleNavigateVideo(video.id);
                                    }}>{formatDate(video.timestamp)}</a>
                            </td>
                            <td>
                                {video.title}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </>
    );
}

export default Videos