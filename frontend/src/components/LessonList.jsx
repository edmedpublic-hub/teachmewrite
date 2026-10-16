// src/components/LessonList.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { lessonsAPI, progressAPI, handleApiError } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const LessonList = () => {
  const { user } = useAuth();
  const [lessons, setLessons] = useState([]);
  const [progressMap, setProgressMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLessonsAndProgress();
  }, []);

  const fetchLessonsAndProgress = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch lessons
      const lessonsData = await lessonsAPI.getAllLessons();
      const lessonsArray = lessonsData.results || lessonsData;
      setLessons(lessonsArray);
      
      // Fetch all progress
      const progressData = await progressAPI.getUserProgress();
      const progressArray = progressData.results || progressData;
      
      // Create progress map
      const map = {};
      progressArray.forEach(progress => {
        map[progress.lesson] = progress;
      });
      setProgressMap(map);
      
    } catch (error) {
      const handledError = handleApiError(error);
      setError(handledError.message);
      console.error('Failed to fetch lessons:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (progress) => {
    if (!progress) {
      return <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded-full">Not Started</span>;
    }
    
    switch(progress.status) {
      case 'completed':
        return <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">Completed</span>;
      case 'in_progress':
        return <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">In Progress</span>;
      default:
        return <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded-full">Not Started</span>;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
        <strong className="font-bold">Error: </strong>
        <span className="block sm:inline">{error}</span>
        <button 
          onClick={fetchLessonsAndProgress}
          className="mt-2 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-green-600 to-teal-600 rounded-lg shadow-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">Your Lessons</h1>
        <p className="text-green-100">
          {user?.tier || 'BASIC'} Tier - Complete lessons to advance your English skills
        </p>
        <p className="text-green-100 text-sm mt-2">
          Total Lessons: {lessons.length}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {lessons.map((lesson) => {
          const progress = progressMap[lesson.id];
          return (
            <Link 
              key={lesson.id} 
              to={`/lessons/${lesson.id}`}
              className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
            >
              <div className="p-6">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-xl font-semibold text-gray-800">{lesson.title}</h3>
                  {getStatusBadge(progress)}
                </div>
                <p className="text-gray-600 mb-4 line-clamp-3">{lesson.description}</p>
                <div className="flex justify-between items-center">
                  <div className="text-sm text-gray-500">
                    {progress?.score && (
                      <span>Score: {progress.score}%</span>
                    )}
                    {progress?.completed_at && (
                      <span className="text-green-600"> ✓ Completed</span>
                    )}
                  </div>
                  <span className="text-blue-600 font-semibold">
                    {progress?.status === 'completed' ? 'Review →' : 'Start Lesson →'}
                  </span>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
      
      {lessons.length === 0 && (
        <div className="bg-white rounded-lg shadow-lg p-12 text-center">
          <p className="text-gray-600">No lessons available for your tier yet.</p>
        </div>
      )}
    </div>
  );
};

export default LessonList;