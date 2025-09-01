
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import brand from '../../static/images/athlos_core_a.jpg';
import '../styles/Navigation.css';

function Navigation() {

    const [coachName,setCoachName] = useState("");

    const navigate = useNavigate();

    const handleLogout = (e) => {
        e.preventDefault();
        console.log("logout called");
        sessionStorage.setItem('userEmail', null);
        sessionStorage.setItem('isLoggedIn', 'false');        
        //redirect
        navigate('/logout');
    }

    const handleVideos = (e) => {
        e.preventDefault();
        navigate('/videos');
    }

    const handleStartStream = (e) => {
        e.preventDefault();
        navigate('/startStream');
    }    

    const handleHome = (e) => {
        e.preventDefault();
        navigate('/');
    }

    useEffect(() => {
        setCoachName(sessionStorage.getItem("username"));
    },[]);

    return (
        <nav className="navbar navbar-expand-lg bg-light">
            <div className="container-fluid d-flex">                
                <a className="navbar-brand" href="#" onClick={handleHome}><img src={brand} style={{height: "50px"}} /></a>
                <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"></span>
                </button>
                <div className="navbar-collapse" id="navbarSupportedContent">
                    <ul className="navbar-nav me-auto mb-2 mb-lg-0">
                        <li className="nav-item">
                            <a className="nav-link active" href="#" onClick={handleHome}>
                                Home
                            </a>
                        </li>
                        <li className="nav-item">
                            <a className="nav-link active" href="#" onClick={handleStartStream}>
                                Start Stream
                            </a>
                        </li>
                        <li className="nav-item">
                            <a className="nav-link active" href="#" onClick={handleVideos}>
                                Videos
                            </a>
                        </li>
                    </ul>
                    <ul className="navbar-nav ms-auto mb-2 mb-lg-0">
                        <li className="nav-item">
                            <a className="nav-link active" href="#" onClick={(e) => e.preventDefault()}>
                                { coachName }
                            </a>
                        </li>
                        <li className="nav-item">
                            <a className="nav-link active" href="#" onClick={handleLogout}>
                                Logout
                            </a>
                        </li>                                                
                    </ul>
                </div>
            </div>
        </nav>        
    );
}

export default Navigation