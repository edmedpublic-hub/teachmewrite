// src/components/TeacherDashboard.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { adaptiveAPI, lessonsAPI, progressAPI, handleApiError } from '../services/api';

const TeacherDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [lessons, setLessons] = useState([]);
  const [studentProgress, setStudentProgress] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [analytics, setAnalytics] = useState({
    totalStudents: 0,
    totalLessons: 0,
    averageCompletion: 0,
    topPerformer: null
  });

  useEffect(() => {
    fetchTeacherData();
  }, []);

  const fetchTeacherData = async () => {
    setLoading(true);
    setError('');
    try {
      // Fetch lessons
      const lessonsData = await lessonsAPI.getAllLessons();
      const lessonsList = lessonsData.results || lessonsData || [];
      setLessons(lessonsList);

      // For now, get mock student data (will be replaced with real student list)
      // In production, this would fetch students from the teacher's classes
      const mockStudents = [
        { id: 1, username: 'student_basic', email: 'basic@example.com', tier: 'BASIC' },
        { id: 2, username: 'student_intermediate', email: 'intermediate@example.com', tier: 'INTERMEDIATE' },
        { id: 3, username: 'student_advanced', email: 'advanced@example.com', tier: 'ADVANCED' },
      ];
      setStudents(mockStudents);

      // Fetch progress for all students (mock for now)
      const progressData = await progressAPI.getUserProgress();
      const progressList = progressData.results || progressData || [];
      setStudentProgress(progressList);

      // Calculate analytics
      const totalLessons = lessonsList.length;
      const completedCount = progressList.filter(p => p.is_completed).length;
      const avgCompletion = totalLessons > 0 ? (completedCount / totalLessons) * 100 : 0;

      setAnalytics({
        totalStudents: mockStudents.length,
        totalLessons: totalLessons,
        averageCompletion: Math.round(avgCompletion),
        topPerformer: progressList.length > 0 ? progressList[0] : null
      });

    } catch (err) {
      const handled = handleApiError(err);
      setError(handled.message);
      console.error('Teacher dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleViewStudent = (student) => {
    setSelectedStudent(student);
  };

  const handleCloseStudentModal = () => {
    setSelectedStudent(null);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getStudentProgressForLesson = (studentId, lessonId) => {
    return studentProgress.find(p => p.user === studentId && p.lesson === lessonId);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center flex-wrap gap-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">📚 Teacher Dashboard</h1>
              <p className="text-sm text-gray-500">
                Welcome back, {user?.username || 'Teacher'}!
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => navigate('/admin/lessons')}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
              >
                ✏️ Manage Lessons
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Students</p>
                <p className="text-3xl font-bold text-blue-600">{analytics.totalStudents}</p>
              </div>
              <div className="text-3xl">👥</div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Lessons</p>
                <p className="text-3xl font-bold text-green-600">{analytics.totalLessons}</p>
              </div>
              <div className="text-3xl">📖</div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Avg Completion</p>
                <p className="text-3xl font-bold text-purple-600">{analytics.averageCompletion}%</p>
              </div>
              <div className="text-3xl">📊</div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Active Lessons</p>
                <p className="text-3xl font-bold text-orange-600">{lessons.filter(l => l.is_published).length}</p>
              </div>
              <div className="text-3xl">✅</div>
            </div>
          </div>
        </div>

        {/* Lessons Overview */}
        <div className="bg-white rounded-xl shadow-lg mb-8">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold text-gray-800">📚 Lesson Progress Overview</h2>
            <p className="text-sm text-gray-500 mt-1">Track student progress across all lessons</p>
          </div>
          <div className="p-6">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-semibold text-gray-600">Lesson</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-600">Tier</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-600">Status</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-600">Questions</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-600">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {lessons.slice(0, 10).map((lesson) => (
                    <tr key={lesson.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4">{lesson.title}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          lesson.tier === 'BASIC' ? 'bg-blue-100 text-blue-700' :
                          lesson.tier === 'INTERMEDIATE' ? 'bg-green-100 text-green-700' :
                          lesson.tier === 'ADVANCED' ? 'bg-purple-100 text-purple-700' :
                          'bg-orange-100 text-orange-700'
                        }`}>
                          {lesson.tier}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          lesson.is_published ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                        }`}>
                          {lesson.is_published ? 'Published' : 'Draft'}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-gray-600">
                        {lesson.practice_questions?.length || 0}
                      </td>
                      <td className="py-3 px-4">
                        <button
                          onClick={() => navigate(`/admin/lessons/${lesson.id}`)}
                          className="text-sm text-blue-600 hover:underline"
                        >
                          Edit →
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Student List */}
        <div className="bg-white rounded-xl shadow-lg">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold text-gray-800">👨‍🎓 Student Roster</h2>
            <p className="text-sm text-gray-500 mt-1">Click on a student to view detailed progress</p>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {students.map((student) => (
                <div
                  key={student.id}
                  onClick={() => handleViewStudent(student)}
                  className="border rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold">
                      {student.username?.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold text-gray-800">{student.username}</p>
                      <p className="text-xs text-gray-500">{student.tier} Tier</p>
                    </div>
                    <div className="text-gray-400">→</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>

      {/* Student Progress Modal */}
      {selectedStudent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="sticky top-0 bg-white p-6 border-b flex justify-between items-center">
              <div>
                <h3 className="text-xl font-bold">{selectedStudent.username}</h3>
                <p className="text-sm text-gray-500">{selectedStudent.email}</p>
              </div>
              <button
                onClick={handleCloseStudentModal}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg text-center">
                  <p className="text-sm text-blue-600">Tier</p>
                  <p className="text-xl font-bold text-blue-800">{selectedStudent.tier}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <p className="text-sm text-green-600">Lessons Completed</p>
                  <p className="text-xl font-bold text-green-800">
                    {studentProgress.filter(p => p.is_completed).length}
                  </p>
                </div>
              </div>
              
              <div>
                <h4 className="font-semibold mb-3">Lesson Progress</h4>
                <div className="space-y-2">
                  {lessons.slice(0, 5).map((lesson) => {
                    const progress = getStudentProgressForLesson(selectedStudent.id, lesson.id);
                    return (
                      <div key={lesson.id} className="flex items-center justify-between">
                        <span className="text-sm">{lesson.title}</span>
                        <div className="flex items-center space-x-3">
                          <div className="w-32 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 rounded-full h-2 transition-all"
                              style={{ width: `${progress?.mastery_score || 0}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium w-12">
                            {progress?.mastery_score || 0}%
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TeacherDashboard;