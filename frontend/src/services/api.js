// src/services/api.js
import axios from 'axios';

const API_BASE_URL = '/teach-me-write/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`/teach-me-write/api/auth/token/refresh/`, {
          refresh: refreshToken,
        });
        
        localStorage.setItem('access_token', response.data.access);
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

// ============================================
// AUTHENTICATION API
// ============================================

export const authAPI = {
  login: async (username, password) => {
    const response = await api.post('/auth/token/', { username, password });
    if (response.data.access) {
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
    }
    return response.data;
  },
  register: async (userData) => {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
  getCurrentUser: async () => {
    const response = await api.get('/v1/users/me/');
    return response.data;
  },
  updateProfile: async (profileData) => {
    const response = await api.patch('/v1/users/me/', profileData);
    return response.data;
  },
};

// ============================================
// LESSONS API
// ============================================

export const lessonsAPI = {
  getAllLessons: async () => {
    const response = await api.get('/v1/lessons/');
    return response.data;
  },
  getLessonById: async (id) => {
    const response = await api.get(`/v1/lessons/${id}/`);
    return response.data;
  },
  getLessonsByTier: async (tier) => {
    const response = await api.get(`/v1/lessons/?tier=${tier}`);
    return response.data;
  },
  getLessonContent: async (id) => {
    const response = await api.get(`/v1/lessons/${id}/content/`);
    return response.data;
  },
};

// ============================================
// PROGRESS API
// ============================================

export const progressAPI = {
  getUserProgress: async () => {
    const response = await api.get('/v1/progress/');
    return response.data.results || response.data;
  },
  updateLessonProgress: async (lessonId, status, score = null) => {
    const response = await api.post('/v1/progress/', {
      lesson_id: lessonId,
      status: status,
      score: score,
    });
    return response.data;
  },
  getLessonProgress: async (lessonId) => {
    const response = await api.get(`/v1/progress/?lesson=${lessonId}`);
    const results = response.data.results || response.data;
    return results && results.length > 0 ? results[0] : { status: 'not_started', score: null };
  },
  getOverallProgress: async () => {
    const response = await api.get('/v1/progress/overall/');
    return response.data;
  },
};

// ============================================
// DASHBOARD API
// ============================================

export const dashboardAPI = {
  getDashboardData: async () => {
    return { message: "Dashboard data not implemented yet" };
  },
  getRecentActivity: async () => {
    return [];
  },
  getAchievements: async () => {
    return [];
  },
  getRecommendations: async () => {
    return [];
  },
};

// ============================================
// WRITING API (Legacy - to be replaced)
// ============================================

export const writingAPI = {
  submitPractice: async (lessonId, content, type = 'practice') => {
    console.warn('Writing submission endpoint not implemented yet');
    return {
      id: Date.now(),
      lesson_id: lessonId,
      content: content,
      type: type,
      score: Math.floor(Math.random() * 30) + 70,
      feedback: "Mock response: Writing endpoint pending."
    };
  },
  getSubmissions: async () => [],
  getFeedback: async (submissionId) => ({
    score: 85,
    strengths: "Good structure",
    improvements: "Work on variety"
  }),
};

// ============================================
// AI API
// ============================================

export const aiAPI = {
  getWritingAnalysis: async (text) => ({
    grammar_feedback: "Basic grammar check pending",
    suggestions: ["Vary sentence structure"],
    score: Math.floor(Math.random() * 30) + 70,
  }),
};

// ============================================
// REPORTS API
// ============================================

export const reportsAPI = {
  getMasteryReport: async () => {
    const response = await api.get('/v1/reports/mastery/');
    return response.data;
  },
  getDetailedReport: async () => {
    const response = await api.get('/v1/reports/detailed/');
    return response.data;
  },
  downloadReport: async (format = 'pdf') => {
    const response = await api.get(`/v1/reports/download/?format=${format}`, { responseType: 'blob' });
    return response.data;
  },
};

// ============================================
// CERTIFICATES API
// ============================================

export const certificatesAPI = {
  getCertificates: async () => {
    const response = await api.get('/v1/certificates/');
    return response.data;
  },
  downloadCertificate: async (id, format = 'pdf') => {
    const response = await api.get(`/v1/certificates/${id}/download/?format=${format}`, { responseType: 'blob' });
    return response.data;
  },
  generateCertificate: async (tier) => {
    const response = await api.post('/v1/certificates/generate/', { tier });
    return response.data;
  },
};

// ============================================
// ADAPTIVE LEARNING API (NEW)
// ============================================

export const adaptiveAPI = {
  // Units
  getAllUnits: async () => {
    const response = await api.get('/v1/units/');
    return response.data;
  },
  getUnitById: async (id) => {
    const response = await api.get(`/v1/units/${id}/`);
    return response.data;
  },

  // Lesson Units
  getLessonUnit: async (unitId, lessonId) => {
    const response = await api.get(`/v1/adaptive/units/${unitId}/lessons/${lessonId}/`);
    return response.data;
  },

  // Practice
  getPracticeQuestions: async (lessonUnitId, numQuestions = 5) => {
    const response = await api.get(`/v1/adaptive/practice/${lessonUnitId}/questions/?num_questions=${numQuestions}`);
    return response.data;
  },
  submitPractice: async (lessonUnitId, answers, timeSpent = 0) => {
    const response = await api.post(`/v1/adaptive/practice/${lessonUnitId}/submit/`, {
      answers: answers,
      time_spent: timeSpent
    });
    return response.data;
  },

  // Test
  getTestQuestions: async (lessonUnitId, numQuestions = 8) => {
    const response = await api.get(`/v1/adaptive/test/${lessonUnitId}/questions/?num_questions=${numQuestions}`);
    return response.data;
  },
  submitTest: async (lessonUnitId, answers, timeSpent = 0) => {
    const response = await api.post(`/v1/adaptive/test/${lessonUnitId}/submit/`, {
      answers: answers,
      time_spent: timeSpent
    });
    return response.data;
  },

  // Progress
  getStudentProgress: async (lessonUnitId) => {
    const response = await api.get(`/v1/student-progress/?lesson_unit=${lessonUnitId}`);
    return response.data;
  },
};

// ============================================
// ERROR HANDLER
// ============================================

export const handleApiError = (error) => {
  if (error.response) {
    const message = error.response.data?.detail || error.response.data?.message || 'An error occurred';
    return { error: true, message, status: error.response.status };
  }
  return { error: true, message: error.message || 'Network error', status: error.request ? 0 : null };
};

export default api;
