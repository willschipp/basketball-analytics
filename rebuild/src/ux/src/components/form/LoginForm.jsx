import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom';

import Banner from '../layout/Banner';

function LoginForm() {

    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState("")

    const navigate = useNavigate();

    const handleLogin = (e) => {
        e.preventDefault()
        // Simple validation example
        if (!email) {
            setError("Email is required")
            return
        }
        if (!password) {
            setError("Password is required")
            return
        }
        setError("")
        // Check credentials
        if (email === 'will@athloscore.ai' && password === 'Welcome!') {
            // Set session variable accessible from other pages
            sessionStorage.setItem('userEmail', email);
            sessionStorage.setItem('isLoggedIn', 'true');
            sessionStorage.setItem('username','Will');

            // You can redirect the user or do other actions here
            navigate('/', { replace: true });
        } else {
            alert("Invalid email or password");
        }// end if
    }
    
    // className={`form-control ${error.includes("Email") ? "is-invalid" : ""}`}
    // className={`form-control ${error.includes("Password") ? "is-invalid" : ""}`}

//<div className="d-flex vh-100 justify-content-center align-items-center">

    return (
        <>
            <div className="container vh-100 d-flex flex-column justify-content-center align-items-center">
    
    {/* Banner as a wide card above */}
    <div className="card w-100 mb-4" style={{ maxWidth: "680px" , borderColor: "#162948"}}>
        <div className="card-body text-center" style={{ backgroundColor: "#162948", color: "white" }}>
            <Banner />
        </div>
    </div>

    {/* Two side-by-side cards below */}
    <div className="d-flex">
        {/* Login Card */}
        <div className="card shadow" style={{ width: "320px" }}>
            <div className="card-body" style={{ backgroundColor: "white", color: "#162948" }}>
                <h2 className="text-center mb-4">Login</h2>
                <form onSubmit={handleLogin}>
                    <div className="mb-3">
                        <label htmlFor="email-input" className="form-label">
                            Email <span className="text-danger">(required)</span>
                        </label>
                        <input
                            id="email-input"
                            type="email"
                            className="form-control"
                            placeholder="Enter your email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                        {error.includes("Email") && (
                            <div className="invalid-feedback">{error}</div>
                        )}
                    </div>

                    {/* Password Field */}
                    <div className="mb-3">
                        <label htmlFor="password-input" className="form-label">
                            Password <span className="text-danger">(required)</span>
                        </label>
                        <input
                            id="password-input"
                            type="password"
                            className="form-control"
                            placeholder="Enter your password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                        {error.includes("Password") && (
                            <div className="invalid-feedback">{error}</div>
                        )}
                    </div>

                    {/* Login Button */}
                    <button
                        type="submit"
                        className="btn btn-outline-secondary w-100"
                        style={{ backgroundColor: "#f15e22", color: "white", borderColor: "#f15e22" }} >
                        Log in
                    </button>
                </form>
            </div>
        </div>

        {/* Side Content Card */}
        <div
            className="card"
            style={{
                width: "320px",
                backgroundColor: "transparent",
                color: "white",
                border: "none",
                boxShadow: "none",
                marginLeft: "30px",
                marginTop: "10px"
            }} >
            <h2>AI-Powered Game Analysis for Coaches</h2>
            <br />
            <ul>
                <li><h5>Gain Strategic Insights</h5></li>
                <li><h5>Enhance Team Performance</h5></li>
                <li><h5>Save Time on Prep</h5></li>
            </ul>
        </div>
    </div>
</div>       

        </>
    );
}

export default LoginForm