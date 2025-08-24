import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';


function Logout() {

    const navigate = useNavigate();

    useEffect(() => {
        sessionStorage.setItem('userEmail', null);
        sessionStorage.setItem('isLoggedIn', 'false');
    }, []);

    return (
        <>
            <h3>Logged Out!</h3>
        </>
    );
}

export default Logout