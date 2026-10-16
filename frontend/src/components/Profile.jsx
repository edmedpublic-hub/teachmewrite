// src/components/Profile.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { adaptiveAPI, lessonsAPI, progressAPI, certificatesAPI, handleApiError } from '../services/api';

const Profile = () => {
  const { user, updateProfile } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [stats, setStats] = useState({
    totalLessons: 0,
    completedLessons: 0,
    averageScore: 0,
    totalQuestions: 0,
    certificates: 0,
    joinedDate: null
  });
  const [masteredLessons, setMasteredLessons] = useState([]);
  const [certificates, setCertificates] = useState([]);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    bio: user?.bio || '',
  });

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch lessons and progress
      const [lessonsData, progressData, certsData] = await Promise.all([
        lessonsAPI.getAllLessons(),
        progressAPI.getUserProgress(),
        certificatesAPI.getCertificates().catch(() => [])
      ]);

      const lessons = lessonsData.results || lessonsData || [];
      const progress = progressData.results || progressData || [];
      const certs = certsData.results || certsData || [];

      // Calculate statistics
      const completedLessons = progress.filter(p => p.is_completed).length;
      const completedScores = progress.filter(p => p.mastery_score > 0).map(p => p.mastery_score);
      const avgScore = completedScores.length > 0 
        ? Math.round(completedScores.reduce((a, b) => a + b, 0) / completedScores.length)
        : 0;

      // Total questions answered (mock for now)
      const totalQuestions = progress.reduce((sum, p) => sum + (p.practice_attempts || 0) * 5, 0);

      setStats({
        totalLessons: lessons.length,
        completedLessons,
        averageScore: avgScore,
        totalQuestions,
        certificates: certs.length,
        joinedDate: new Date(Date.now() - 30 * 86400000) // Mock joined date
      });

      // Get mastered lessons
      const mastered = progress.filter(p => p.is_mastered).map(p => ({
        id: p.lesson,
        title: p.lesson_title,
        score: p.mastery_score,
        completed_at: p.completed_at
      }));
      setMasteredLessons(mastered);

      // Get certificates
      setCertificates(certs);

    } catch (err) {
      const handled = handleApiError(err);
      setError(handled.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(null);
    
    const result = await updateProfile(formData);
    
    if (result.success) {
      setSuccess('Profile updated successfully!');
      setIsEditing(false);
    } else {
      setError(result.error || 'Failed to update profile');
    }
    
    setSaving(false);
  };

  const formatDate = (date) => {
    if (!date) return 'N/A';
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
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
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl shadow-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">My Profile</h1>
        <p className="text-purple-100">Manage your account and track your learning journey</p>
      </div>

      {/* Profile Card */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="bg-gradient-to-r from-blue-500 to-purple-500 px-6 py-8 text-white">
          <div className="flex items-center space-x-4">
            <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center text-3xl font-bold text-purple-600">
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div>
              <h2 className="text-2xl font-bold">{user?.username}</h2>
              <p className="text-blue-100">Member since {formatDate(stats.joinedDate)}</p>
              <div className="mt-2">
                <span className="inline-block px-3 py-1 bg-white/20 rounded-full text-sm">
                  {user?.tier || 'BASIC'} Tier
                </span>
              </div>
            </div>
          </div>
        </div>

        {!isEditing ? (
          <div className="p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold">Personal Information</h3>
              <button
                onClick={() => setIsEditing(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Edit Profile
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="text-sm text-gray-500">Username</label>
                <p className="text-lg font-medium">{user?.username}</p>
              </div>
              <div>
                <label className="text-sm text-gray-500">Email</label>
                <p className="text-lg font-medium">{user?.email || 'Not provided'}</p>
              </div>
              <div>
                <label className="text-sm text-gray-500">First Name</label>
                <p className="text-lg font-medium">{user?.first_name || 'Not provided'}</p>
              </div>
              <div>
                <label className="text-sm text-gray-500">Last Name</label>
                <p className="text-lg font-medium">{user?.last_name || 'Not provided'}</p>
              </div>
              <div className="md:col-span-2">
                <label className="text-sm text-gray-500">Bio</label>
                <p className="text-lg font-medium">{user?.bio || 'No bio yet'}</p>
              </div>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="p-6">
            {error && (
              <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
                {error}
              </div>
            )}
            {success && (
              <div className="mb-4 p-3 bg-green-100 text-green-700 rounded-lg">
                {success}
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  disabled
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Bio</label>
                <textarea
                  name="bio"
                  value={formData.bio}
                  onChange={handleChange}
                  rows="3"
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            
            <div className="mt-6 flex gap-3">
              <button
                type="submit"
                disabled={saving}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
              <button
                type="button"
                onClick={() => setIsEditing(false)}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>

      {/* Statistics Card */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <div className="bg-white rounded-xl shadow-lg p-6 text-center">
          <div className="text-3xl mb-2">📚</div>
          <div className="text-2xl font-bold text-blue-600">{stats.completedLessons}/{stats.totalLessons}</div>
          <div className="text-sm text-gray-600">Lessons Completed</div>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6 text-center">
          <div className="text-3xl mb-2">⭐</div>
          <div className="text-2xl font-bold text-green-600">{stats.averageScore}%</div>
          <div className="text-sm text-gray-600">Average Score</div>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6 text-center">
          <div className="text-3xl mb-2">❓</div>
          <div className="text-2xl font-bold text-purple-600">{stats.totalQuestions}</div>
          <div className="text-sm text-gray-600">Questions Answered</div>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6 text-center">
          <div className="text-3xl mb-2">🏆</div>
          <div className="text-2xl font-bold text-orange-600">{stats.certificates}</div>
          <div className="text-sm text-gray-600">Certificates Earned</div>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6 text-center">
          <div className="text-3xl mb-2">🔥</div>
          <div className="text-2xl font-bold text-red-600">7</div>
          <div className="text-sm text-gray-600">Day Streak</div>
        </div>
      </div>

      {/* Mastered Lessons */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold mb-4">🏅 Mastered Lessons</h2>
        {masteredLessons.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {masteredLessons.map((lesson) => (
              <div key={lesson.id} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div>
                  <span className="font-medium">{lesson.title}</span>
                  <div className="text-sm text-green-600">Score: {lesson.score}%</div>
                </div>
                <span className="text-green-600">✓ Mastered</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No mastered lessons yet. Complete lessons to see them here!</p>
        )}
      </div>

      {/* Certificates */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold mb-4">🎓 Certificates Earned</h2>
        {certificates.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {certificates.map((cert) => (
              <div key={cert.id} className="border rounded-lg p-4 text-center hover:shadow-md transition-shadow">
                <div className="text-3xl mb-2">📜</div>
                <div className="font-semibold">{cert.tier} Tier</div>
                <div className="text-sm text-gray-500">Issued: {formatDate(cert.issue_date)}</div>
                <Link
                  to={`/certificates`}
                  className="mt-2 inline-block text-sm text-blue-600 hover:underline"
                >
                  View Certificate →
                </Link>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No certificates yet. Complete all lessons in a tier to earn one!</p>
        )}
      </div>
    </div>
  );
};

export default Profile;