import React, { useState } from 'react'
import 'bootstrap/dist/css/bootstrap.min.css'
// import './scss/styles.scss'
import './App.css'

function App() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")

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
    // Place your login logic here
    alert(`Logging in with\nEmail: ${email}\nPassword: ${password}`)
  }

  return (
    <div className="d-flex vh-100 justify-content-center align-items-center">
      <div className="card shadow" style={{ width: "320px" }}>
        <div className="card-body">
          <h2 className="text-center mb-4">Login</h2>
          <form onSubmit={handleLogin}>
            {/* Email Field */}
            <div className="mb-3">
              <label htmlFor="email-input" className="form-label">
                Email <span className="text-danger">(required)</span>
              </label>
              <input
                id="email-input"
                type="email"
                className={`form-control ${error.includes("Email") ? "is-invalid" : ""}`}
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
                className={`form-control ${error.includes("Password") ? "is-invalid" : ""}`}
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              {error.includes("Password") && (
                <div className="invalid-feedback">{error}</div>
              )}
            </div>

            {/* Login Button */}
            <button type="submit" className="btn btn-outline-secondary w-100">
              Log in
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default App
