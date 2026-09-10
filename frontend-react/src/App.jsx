import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import Login from './components/Login';
import Signup from './components/Signup';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Tailor from './pages/Tailor';

const AuthHandler = ({ children }) => {
  const navigate = useNavigate();
  
  useEffect(() => {
    const handleAuthError = () => {
      navigate('/login');
    };
    
    window.addEventListener('auth-error', handleAuthError);
    return () => window.removeEventListener('auth-error', handleAuthError);
  }, [navigate]);
  
  return children;
};

function App() {
  return (
    <BrowserRouter>
      <AuthHandler>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          
          <Route element={<Layout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/tailor" element={<Tailor />} />
          </Route>
        </Routes>
      </AuthHandler>
    </BrowserRouter>
  );
}

export default App;
