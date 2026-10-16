// src/components/LandingPage.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const LandingPage = () => {
  const { isAuthenticated } = useAuth();

  // If already logged in, redirect to dashboard
  if (isAuthenticated) {
    window.location.href = '/dashboard';
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-24">
          <div className="text-center">
            <h1 className="text-5xl lg:text-6xl font-extrabold text-gray-900 mb-4">
              TeachMeWrite
            </h1>
            <p className="text-2xl lg:text-3xl text-gray-600 mb-6">
              English Writing Mastery Platform
            </p>
            <p className="text-xl text-gray-500 max-w-3xl mx-auto mb-12">
              Master English writing for Matric to CSS/Competitive exams. 
              Get AI-powered feedback, track your progress, and earn certificates.
            </p>
            
            <div className="flex justify-center space-x-4">
              <Link
                to="/login"
                className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-lg font-semibold"
              >
                Login
              </Link>
              <Link
                to="/register"
                className="px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-lg font-semibold"
              >
                Register
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Why Choose TeachMeWrite?
          </h2>
          <p className="text-xl text-gray-600">
            Comprehensive platform for Pakistani students
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Feature 1 */}
          <div className="bg-white rounded-lg shadow-lg p-6 text-center">
            <div className="text-5xl mb-4">📚</div>
            <h3 className="text-xl font-semibold mb-2">4-Tier Learning</h3>
            <p className="text-gray-600">
              BASIC, INTERMEDIATE, ADVANCED, and PROFESSIONAL levels tailored to your needs
            </p>
          </div>

          {/* Feature 2 */}
          <div className="bg-white rounded-lg shadow-lg p-6 text-center">
            <div className="text-5xl mb-4">🤖</div>
            <h3 className="text-xl font-semibold mb-2">AI-Powered Feedback</h3>
            <p className="text-gray-600">
              Get instant AI analysis on your writing with grammar and style suggestions
            </p>
          </div>

          {/* Feature 3 */}
          <div className="bg-white rounded-lg shadow-lg p-6 text-center">
            <div className="text-5xl mb-4">🎓</div>
            <h3 className="text-xl font-semibold mb-2">CSS/Exam Focus</h3>
            <p className="text-gray-600">
              Specialized content for competitive exams including CSS, PMS, and NTS
            </p>
          </div>

          {/* Feature 4 */}
          <div className="bg-white rounded-lg shadow-lg p-6 text-center">
            <div className="text-5xl mb-4">📊</div>
            <h3 className="text-xl font-semibold mb-2">Progress Tracking</h3>
            <p className="text-gray-600">
              Monitor your improvement with detailed mastery reports
            </p>
          </div>

          {/* Feature 5 */}
          <div className="bg-white rounded-lg shadow-lg p-6 text-center">
            <div className="text-5xl mb-4">🏆</div>
            <h3 className="text-xl font-semibold mb-2">Certificates</h3>
            <p className="text-gray-600">
              Earn verifiable certificates upon completing each tier
            </p>
          </div>

          {/* Feature 6 */}
          <div className="bg-white rounded-lg shadow-lg p-6 text-center">
            <div className="text-5xl mb-4">💯</div>
            <h3 className="text-xl font-semibold mb-2">Practice Tests</h3>
            <p className="text-gray-600">
              Test your knowledge with timed writing exercises
            </p>
          </div>
        </div>
      </div>

      {/* Demo Accounts Section */}
      <div className="bg-gray-100 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Try Demo Accounts
            </h2>
            <p className="text-xl text-gray-600">
              Explore different tiers before registering
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg p-4 text-center">
              <div className="font-semibold text-blue-600">BASIC</div>
              <div className="text-sm text-gray-500">student_basic</div>
              <div className="text-sm text-gray-500">testpass123</div>
              <div className="text-xs text-gray-400 mt-2">3 lessons</div>
            </div>
            <div className="bg-white rounded-lg p-4 text-center">
              <div className="font-semibold text-green-600">INTERMEDIATE</div>
              <div className="text-sm text-gray-500">student_intermediate</div>
              <div className="text-sm text-gray-500">testpass123</div>
              <div className="text-xs text-gray-400 mt-2">6 lessons</div>
            </div>
            <div className="bg-white rounded-lg p-4 text-center">
              <div className="font-semibold text-purple-600">ADVANCED</div>
              <div className="text-sm text-gray-500">student_advanced</div>
              <div className="text-sm text-gray-500">testpass123</div>
              <div className="text-xs text-gray-400 mt-2">9 lessons</div>
            </div>
            <div className="bg-white rounded-lg p-4 text-center">
              <div className="font-semibold text-red-600">PROFESSIONAL</div>
              <div className="text-sm text-gray-500">student_css</div>
              <div className="text-sm text-gray-500">testpass123</div>
              <div className="text-xs text-gray-400 mt-2">12 lessons</div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p>© 2024 TeachMeWrite - English Writing Mastery for Pakistani Students</p>
          <p className="text-sm text-gray-400 mt-2">Preparing for Matric, Intermediate, and CSS/Competitive Exams</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;