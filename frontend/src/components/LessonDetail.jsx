// src/components/LessonDetail.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { lessonsAPI, progressAPI, handleApiError } from '../services/api';

const LessonDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState(null);
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLessonAndProgress();
  }, [id]);

  const fetchLessonAndProgress = async () => {
    setLoading(true);
    try {
      const [lessonData, progressData] = await Promise.all([
        lessonsAPI.getLessonById(id),
        progressAPI.getLessonProgress(id).catch(() => null)
      ]);
      setLesson(lessonData);
      setProgress(progressData);
    } catch (error) {
      const handledError = handleApiError(error);
      setError(handledError.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStartPractice = () => {
    navigate(`/writing/${id}`);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !lesson) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <p>{error || 'Lesson not found'}</p>
        <button onClick={() => navigate('/lessons')} className="mt-2 bg-red-500 text-white px-4 py-2 rounded">
          Back to Lessons
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-3xl font-bold mb-4">{lesson.title}</h1>
        
        <div className="prose max-w-none mb-6">
          <h3 className="text-lg font-semibold mb-2">Lesson Content</h3>
          <div className="text-gray-700 leading-relaxed">
            {lesson.content || lesson.description || "Lesson content will appear here."}
          </div>
        </div>
        
        {lesson.prompt && (
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">Writing Prompt:</h3>
            <p className="text-blue-800">{lesson.prompt}</p>
          </div>
        )}
        
        {progress && progress.score && (
          <div className="mt-4 p-3 bg-green-50 rounded-lg">
            <p className="text-green-800">
              <strong>Your Best Score:</strong> {progress.score}%
            </p>
          </div>
        )}
        
        <div className="mt-8 flex justify-between">
          <button
            onClick={() => navigate('/lessons')}
            className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Back to Lessons
          </button>
          <button
            onClick={handleStartPractice}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Start Writing Practice
          </button>
        </div>
      </div>
    </div>
  );
};

export default LessonDetail;