// src/services/aiService.js

const AI_API_URL = import.meta.env.VITE_AI_API_URL || "https://teachmewrite-ai-195673983724.asia-south1.run.app";

export const aiService = {
  getWritingFeedback: async (studentText, level) => {
    const token = localStorage.getItem('access_token');

    if (!token) {
      throw new Error("Authentication required. Please log in.");
    }

    const response = await fetch(`${AI_API_URL}/feedback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({
        student_text: studentText,
        level: parseInt(level)
      }),
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Session expired. Please log in again.");
      }
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "Failed to get AI feedback.");
    }

    return response.json();
  }
};
