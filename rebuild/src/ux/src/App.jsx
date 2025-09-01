import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'

import Footer from './components/layout/Footer';
import Home from './components/pages/Home';
import LoginForm from './components/form/LoginForm';
import Navigation from './components/layout/Navigation';
import Streamer from './components/pages/Streamer';
import Videos from './components/pages/Videos';
import VideoViewer from './components/pages/VideoViewer';

const ProtectedRoute = ({ children }) => {
  const isLoggedIn = sessionStorage.getItem('isLoggedIn') === 'true';
  if (!isLoggedIn) {
    return <Navigate to="/login" replace />; //redirect to login
  }
  return (
    <>
      <div className="wrapper">
        <Navigation/>
        <div className="content">
          {children}
        </div>        
        <Footer />        
      </div>
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

        <Route path="/videos/viewer" element={
            <ProtectedRoute>
              <VideoViewer/>
            </ProtectedRoute>
        } />                
        
        <Route path="/login" element={<LoginForm />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>

    </Router>
  )
}

export default App
