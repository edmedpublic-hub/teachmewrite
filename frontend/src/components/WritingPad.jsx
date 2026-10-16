// src/components/WritingPad.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { lessonsAPI, writingAPI, aiAPI, handleApiError } from '../services/api';


const WritingPad = () => {
  const { lessonId } = useParams();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState(null);
  const [content, setContent] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [wordCount, setWordCount] = useState(0);
  const [error, setError] = useState(null);
  const [practiceType, setPracticeType] = useState('practice'); // 'practice' or 'test'
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    fetchLesson();
  }, [lessonId]);

  useEffect(() => {
    // Update word count
    const words = content.trim().split(/\s+/).filter(word => word.length > 0);
    setWordCount(words.length);
  }, [content]);

  const fetchLesson = useCallback(async () => {
  try {
    const lessonData = await lessonsAPI.getLessonById(lessonId);
    setLesson(lessonData);
  } catch (error) {
    const handledError = handleApiError(error);
    setError(handledError.message);
  }
}, [lessonId]); // Only changes if lessonId changes

useEffect(() => {
  fetchLesson();
}, [fetchLesson]);

  const handleSubmit = async () => {
    if (!content.trim()) {
      setError('Please write something before submitting');
      return;
    }

    setSubmitting(true);
    setError(null);
    
    try {
      const submission = await writingAPI.submitPractice(lessonId, content, practiceType);
      
      // Get feedback
      const feedbackData = await writingAPI.getFeedback(submission.id);
      setFeedback(feedbackData);
      
      // Show success message
      alert(`Submission successful! Your score: ${feedbackData.score}%`);
      
      // Reset if practice, navigate if test
      if (practiceType === 'test') {
        navigate('/certificates');
      }
    } catch (error) {
      const handledError = handleApiError(error);
      setError(handledError.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleAIAnalysis = async () => {
    if (!content.trim()) {
      setError('Please write something to analyze');
      return;
    }

    setAnalyzing(true);
    setError(null);
    
    try {
      const analysis = await aiAPI.getWritingAnalysis(content);
      setAiAnalysis(analysis);
    } catch (error) {
      const handledError = handleApiError(error);
      setError(handledError.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const clearContent = () => {
    if (window.confirm('Are you sure you want to clear your writing?')) {
      setContent('');
      setFeedback(null);
      setAiAnalysis(null);
    }
  };

  if (error && !lesson) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <p>{error}</p>
        <button onClick={() => navigate('/lessons')} className="mt-2 bg-red-500 text-white px-4 py-2 rounded">
          Back to Lessons
        </button>
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Lesson Info */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-3xl font-bold mb-2">{lesson.title}</h1>
        <p className="text-gray-600">{lesson.description}</p>
        {lesson.prompt && (
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">Writing Prompt:</h3>
            <p className="text-blue-800">{lesson.prompt}</p>
          </div>
        )}
      </div>

      {/* Practice Type Selection */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex space-x-4">
          <label className="flex items-center">
            <input
              type="radio"
              value="practice"
              checked={practiceType === 'practice'}
              onChange={(e) => setPracticeType(e.target.value)}
              className="mr-2"
            />
            Practice Mode (Unlimited attempts)
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              value="test"
              checked={practiceType === 'test'}
              onChange={(e) => setPracticeType(e.target.value)}
              className="mr-2"
            />
            Test Mode (Graded for certificate)
          </label>
        </div>
      </div>

      {/* Writing Area */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Your Response</h2>
          <div className="text-sm text-gray-600">
            Word count: {wordCount}
          </div>
        </div>
        
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full h-96 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y"
          placeholder="Write your response here... (minimum 100 words recommended)"
          disabled={submitting}
        />
        
        <div className="flex space-x-4 mt-4">
          <button
            onClick={handleSubmit}
            disabled={submitting || !content.trim()}
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {submitting ? 'Submitting...' : `Submit ${practiceType === 'test' ? 'Test' : 'Practice'}`}
          </button>
          
          <button
            onClick={handleAIAnalysis}
            disabled={analyzing || !content.trim()}
            className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {analyzing ? 'Analyzing...' : 'AI Analysis'}
          </button>
          
          <button
            onClick={clearContent}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Clear
          </button>
        </div>
      </div>

      {/* AI Analysis Results */}
      {aiAnalysis && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4">AI Analysis</h2>
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold text-green-700">Grammar & Style</h3>
              <p className="text-gray-700 mt-1">{aiAnalysis.grammar_feedback}</p>
            </div>
            <div>
              <h3 className="font-semibold text-blue-700">Suggestions</h3>
              <ul className="list-disc list-inside mt-1 space-y-1">
                {aiAnalysis.suggestions?.map((suggestion, idx) => (
                  <li key={idx} className="text-gray-700">{suggestion}</li>
                ))}
              </ul>
            </div>
            {aiAnalysis.score && (
              <div className="mt-4 p-3 bg-gray-100 rounded">
                <p className="font-semibold">AI Score: {aiAnalysis.score}/100</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Previous Feedback */}
      {feedback && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <h2 className="text-xl font-bold text-green-800 mb-3">Feedback</h2>
          <div className="space-y-2">
            <p><strong>Score:</strong> {feedback.score}%</p>
            <p><strong>Strengths:</strong> {feedback.strengths}</p>
            <p><strong>Areas for Improvement:</strong> {feedback.improvements}</p>
            {feedback.teacher_notes && (
              <p><strong>Teacher Notes:</strong> {feedback.teacher_notes}</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default WritingPad;