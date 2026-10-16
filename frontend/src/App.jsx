// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import LandingPage from './components/LandingPage';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import UnitBrowser from './components/UnitBrowser';
import LessonTeachingView from './components/LessonTeachingView';
import PracticeView from './components/PracticeView';
import TestView from './components/TestView';
import Profile from './components/Profile';
import Certificates from './components/Certificates';
import MasteryReport from './components/MasteryReport';
import TeacherDashboard from './components/TeacherDashboard';

const PrivateRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  return isAuthenticated ? children : <Navigate to="/login" />;
};

const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  return !isAuthenticated ? children : <Navigate to="/dashboard" />;
};

// Layout with Navbar for protected pages
const ProtectedLayout = ({ children }) => {
  return (
    <>
      <Navbar />
      <div className="pt-4">
        {children}
      </div>
    </>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router basename="/teach-me-write">
        <div className="min-h-screen bg-gray-50">
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={
              <PublicRoute>
                <Login />
              </PublicRoute>
            } />
            <Route path="/register" element={
              <PublicRoute>
                <Register />
              </PublicRoute>
            } />
            
            {/* Protected Routes with Navbar */}
            <Route path="/dashboard" element={
              <PrivateRoute>
                <ProtectedLayout>
                  <Dashboard />
                </ProtectedLayout>
              </PrivateRoute>
            } />
            
            <Route path="/learn" element={
              <PrivateRoute>
                <ProtectedLayout>
                  <UnitBrowser />
                </ProtectedLayout>
              </PrivateRoute>
            } />
            
            <Route path="/learn/unit/:unitId/lesson/:lessonId" element={
              <PrivateRoute>
                <ProtectedLayout>
                  <LessonTeachingView />
                </ProtectedLayout>
              </PrivateRoute>
            } />
            
            <Route path="/practice/:lessonUnitId" element={
              <PrivateRoute>
                <ProtectedLayout>
                  <PracticeView />
                </ProtectedLayout>
              </PrivateRoute>
            } />
            
            <Route path="/test/:lessonUnitId" element={
              <PrivateRoute>
                <ProtectedLayout>
                  <TestView />
                </ProtectedLayout>
              </PrivateRoute>
            } />
            
            <Route path="/profile" element={
              <PrivateRoute>
                <ProtectedLayout>
                  <Profile />
                </ProtectedLayout>
              </PrivateRoute>
            } />
            
            <Route path="/certificates" element={
              <PrivateRoute>
                <ProtectedLayout>
                  <Certificates />
                </ProtectedLayout>
              </PrivateRoute>
            } />
            <Route path="/teacher/dashboard" element={
              <PrivateRoute>
                <ProtectedLayout>
                  <TeacherDashboard />
              </ProtectedLayout>
            </PrivateRoute>
            } />
            <Route path="/reports" element={
              <PrivateRoute>
                <ProtectedLayout>
                  <MasteryReport />
                </ProtectedLayout>
              </PrivateRoute>
            } />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
