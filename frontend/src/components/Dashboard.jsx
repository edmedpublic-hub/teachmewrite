// src/components/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { adaptiveAPI, lessonsAPI, progressAPI, handleApiError } from '../services/api';

const Dashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    totalLessons: 0,
    completedLessons: 0,
    averageScore: 0,
    totalPracticeTime: 0,
    currentStreak: 0,
    certificates: 0
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [weakConcepts, setWeakConcepts] = useState([]);
  const [nextLesson, setNextLesson] = useState(null);
  const [tierProgress, setTierProgress] = useState({
    BASIC: 0,
    INTERMEDIATE: 0,
    ADVANCED: 0,
    PROFESSIONAL: 0
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch all data in parallel
      const [lessonsData, progressData, unitsData] = await Promise.all([
        lessonsAPI.getAllLessons(),
        progressAPI.getUserProgress(),
        adaptiveAPI.getAllUnits().catch(() => ({ results: [] }))
      ]);

      const lessons = lessonsData.results || lessonsData || [];
      const progress = progressData.results || progressData || [];
      const units = unitsData.results || unitsData || [];

      // Calculate statistics
      const completedLessons = progress.filter(p => p.is_completed).length;
      const totalLessons = lessons.length;
      const completedScores = progress.filter(p => p.mastery_score > 0).map(p => p.mastery_score);
      const avgScore = completedScores.length > 0 
        ? Math.round(completedScores.reduce((a, b) => a + b, 0) / completedScores.length)
        : 0;

      setStats({
        totalLessons,
        completedLessons,
        averageScore: avgScore,
        totalPracticeTime: Math.floor(Math.random() * 120) + 30, // Mock for now
        currentStreak: Math.floor(Math.random() * 7) + 1, // Mock for now
        certificates: 0
      });

      // Calculate tier progress
      const tierStats = { BASIC: 0, INTERMEDIATE: 0, ADVANCED: 0, PROFESSIONAL: 0 };
      lessons.forEach(lesson => {
        const lessonProgress = progress.find(p => p.lesson === lesson.id);
        if (lessonProgress?.is_completed) {
          tierStats[lesson.tier] = (tierStats[lesson.tier] || 0) + 1;
        }
      });
      setTierProgress(tierStats);

      // Find next lesson (first incomplete lesson)
      const nextIncomplete = lessons.find(lesson => {
        const lessonProgress = progress.find(p => p.lesson === lesson.id);
        return !lessonProgress?.is_completed;
      });
      setNextLesson(nextIncomplete || null);

      // Mock recent activity (will be replaced with real data later)
      setRecentActivity([
        { type: 'practice', title: 'Basic Sentence Structure', score: 85, date: new Date() },
        { type: 'test', title: 'Parts of Speech', score: 92, date: new Date(Date.now() - 86400000) },
      ]);

      // Mock weak concepts
      setWeakConcepts(['Subject-Verb Agreement', 'Punctuation', 'Sentence Structure']);

    } catch (err) {
      const handled = handleApiError(err);
      setError(handled.message);
    } finally {
      setLoading(false);
    }
  };

  const getTierColor = (tier) => {
    const colors = {
      BASIC: 'blue',
      INTERMEDIATE: 'green',
      ADVANCED: 'purple',
      PROFESSIONAL: 'orange'
    };
    return colors[tier] || 'gray';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">
          Welcome back, {user?.username}!
        </h1>
        <p className="text-blue-100">
          You're on a {stats.currentStreak}-day learning streak! 🔥
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-lg p-6 text-center">
          <div className="text-3xl mb-2">📚</div>
          <div className="text-3xl font-bold text-blue-600">{stats.completedLessons}/{stats.totalLessons}</div>
          <div className="text-gray-600 text-sm">Lessons Completed</div>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6 text-center">
          <div className="text-3xl mb-2">⭐</div>
          <div className="text-3xl font-bold text-green-600">{stats.averageScore}%</div>
          <div className="text-gray-600 text-sm">Average Score</div>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6 text-center">
          <div className="text-3xl mb-2">⏱️</div>
          <div className="text-3xl font-bold text-purple-600">{stats.totalPracticeTime} min</div>
          <div className="text-gray-600 text-sm">Total Practice Time</div>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6 text-center">
          <div className="text-3xl mb-2">🏆</div>
          <div className="text-3xl font-bold text-orange-600">{stats.certificates}</div>
          <div className="text-gray-600 text-sm">Certificates Earned</div>
        </div>
      </div>

      {/* Tier Progress */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold mb-4">🎯 Tier Progress</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {Object.entries(tierProgress).map(([tier, count]) => {
            const color = getTierColor(tier);
            const totalForTier = tier === 'BASIC' ? 5 : tier === 'INTERMEDIATE' ? 5 : tier === 'ADVANCED' ? 5 : 5;
            const percentage = (count / totalForTier) * 100;
            return (
              <div key={tier} className="text-center">
                <div className={`text-${color}-600 font-semibold mb-2`}>{tier}</div>
                <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                  <div 
                    className={`bg-${color}-600 rounded-full h-2 transition-all duration-500`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
                <div className="text-sm text-gray-600">{count}/{totalForTier} mastered</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Next Lesson & Weak Concepts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Next Lesson */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4">📖 Next Recommended Lesson</h2>
          {nextLesson ? (
            <div>
              <h3 className="font-semibold text-lg">{nextLesson.title}</h3>
              <p className="text-gray-600 text-sm mt-1">{nextLesson.description}</p>
              <Link
                to={`/lessons/${nextLesson.id}`}
                className="mt-4 inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Continue Learning →
              </Link>
            </div>
          ) : (
            <p className="text-gray-500">🎉 Congratulations! You've completed all lessons!</p>
          )}
        </div>

        {/* Weak Concepts */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4">📚 Areas to Improve</h2>
          {weakConcepts.length > 0 ? (
            <div className="space-y-2">
              {weakConcepts.map((concept, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 bg-yellow-50 rounded-lg">
                  <span className="text-yellow-800">{concept}</span>
                  <span className="text-xs text-yellow-600">Needs Practice</span>
                </div>
              ))}
              <Link
                to="/learn"
                className="mt-4 inline-block text-sm text-blue-600 hover:underline"
              >
                Practice these concepts →
              </Link>
            </div>
          ) : (
            <p className="text-gray-500">✨ Great job! No weak areas detected.</p>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold mb-4">🕐 Recent Activity</h2>
        {recentActivity.length > 0 ? (
          <div className="space-y-3">
            {recentActivity.map((activity, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 border-b last:border-0">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{activity.type === 'practice' ? '✍️' : '📝'}</span>
                    <span className="font-medium">{activity.title}</span>
                  </div>
                  <div className="text-sm text-gray-500">
                    {activity.date.toLocaleDateString()}
                  </div>
                </div>
                <div className="text-right">
                  <span className={`font-semibold ${activity.score >= 70 ? 'text-green-600' : 'text-orange-600'}`}>
                    {activity.score}%
                  </span>
                  <div className="text-xs text-gray-400">{activity.type}</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No recent activity. Start learning!</p>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Link
          to="/learn"
          className="bg-blue-50 hover:bg-blue-100 rounded-xl p-4 text-center transition-colors"
        >
          <div className="text-2xl mb-1">📚</div>
          <div className="font-medium text-blue-700">Continue Learning</div>
        </Link>
        <Link
          to="/profile"
          className="bg-purple-50 hover:bg-purple-100 rounded-xl p-4 text-center transition-colors"
        >
          <div className="text-2xl mb-1">👤</div>
          <div className="font-medium text-purple-700">My Profile</div>
        </Link>
        <Link
          to="/certificates"
          className="bg-green-50 hover:bg-green-100 rounded-xl p-4 text-center transition-colors"
        >
          <div className="text-2xl mb-1">🏆</div>
          <div className="font-medium text-green-700">Certificates</div>
        </Link>
        <Link
          to="/reports"
          className="bg-orange-50 hover:bg-orange-100 rounded-xl p-4 text-center transition-colors"
        >
          <div className="text-2xl mb-1">📊</div>
          <div className="font-medium text-orange-700">Reports</div>
        </Link>
      </div>
    </div>
  );
};

export default Dashboard;