import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'

import Footer from './components/Footer';
import Home from './components/Home';
import LoginForm from './components/LoginForm';
import Logout from './components/Logout';
import Navigation from './components/Navigation';
import Streamer from './components/Streamer';
import Videos from './components/Videos';

// ProtectedRoute component to wrap protected routes
const ProtectedRoute = ({ children }) => {
  const isLoggedIn = sessionStorage.getItem('isLoggedIn') === 'true';
  if (!isLoggedIn) {
    // Redirect to login if not logged in
    return <Navigate to="/login" replace />;
  }
  return (
    <>
      <Navigation/>
      {children}
    </>);
};

function App() {

  return (
    <Router>  

      <Routes>
        <Route path="/" element={
            <ProtectedRoute>              
              <Home />
            </ProtectedRoute>
          } />
        
        <Route path="/startStream" element={
            <ProtectedRoute>
              <Streamer/>
            </ProtectedRoute>
        } />

        <Route path="/videos" element={
            <ProtectedRoute>
              <Videos/>
            </ProtectedRoute>
        } />        
        
        <Route path="/login" element={<LoginForm />} />
        <Route path="/logout" element={<Logout />} />        
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>

      <Footer />
    </Router>
  )
}

export default App
