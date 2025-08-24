
import { useNavigate } from 'react-router-dom';

import brand from '../static/images/athloscore_a.jpg';
import './styles/Navigation.css';

function Navigation() {

    const navigate = useNavigate();

    const handleLogout = (e) => {
        e.preventDefault();
        console.log("logout called");
        sessionStorage.setItem('userEmail', null);
        sessionStorage.setItem('isLoggedIn', 'false');        
        //redirect
        navigate('/',{ replace: true });
    }

    const handleVideos = (e) => {
        navigate('/videos',{ replace: true });
    }

    const handleStartStream = (e) => {
        navigate('/startStream',{ replace: true });
    }    

    const handleHome = (e) => {
        navigate('/',{ replace: true});
    }

    return (
        <nav className="navbar bg-light">
            <div className="container-fluid d-flex">
                {/* <a className="navbar-brand" href="#"> */}
                <div className="navbar-brand">
                    <a href="#" onClick={handleHome}><img src={brand} style={{height: "50px"}} /></a>
                </div>     
                <div className="ms-auto">
                    <button type="button" className="btn btn-sm btn-outline-secondary" onClick={handleStartStream}>
                        Start Stream
                    </button>
                    <button type="button" className="btn btn-sm btn-outline-secondary" onClick={handleVideos}>
                        Videos
                    </button>                    
                    <button type="button" className="btn btn-sm btn-outline-secondary" onClick={handleLogout}>
                        Logout
                    </button>
                </div>               
            </div>
        </nav>        
    );
}

export default Navigation