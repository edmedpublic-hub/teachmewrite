// src/components/MasteryReport.jsx
import React, { useState, useEffect } from 'react';
import { reportsAPI, handleApiError } from '../services/api';

const MasteryReport = () => {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    fetchReport();
  }, []);

  const fetchReport = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await reportsAPI.getMasteryReport();
      setReport(data);
    } catch (error) {
      const handledError = handleApiError(error);
      setError(handledError.message);
      console.error('Failed to fetch report:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (format = 'pdf') => {
    setDownloading(true);
    try {
      const blob = await reportsAPI.downloadReport(format);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `mastery_report.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      const handledError = handleApiError(error);
      alert(`Download failed: ${handledError.message}`);
    } finally {
      setDownloading(false);
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
          onClick={fetchReport}
          className="mt-2 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg shadow-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">Mastery Report</h1>
        <p className="text-blue-100">Track your progress and achievements</p>
      </div>

      {report && (
        <>
          {/* Overall Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="text-center">
                <div className="text-4xl font-bold text-blue-600 mb-2">
                  {report.overall_score || 0}%
                </div>
                <div className="text-gray-600">Overall Mastery Score</div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="text-center">
                <div className="text-4xl font-bold text-green-600 mb-2">
                  {report.completed_lessons || 0}
                </div>
                <div className="text-gray-600">Completed Lessons</div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="text-center">
                <div className="text-4xl font-bold text-purple-600 mb-2">
                  {report.total_practices || 0}
                </div>
                <div className="text-gray-600">Writing Practices</div>
              </div>
            </div>
          </div>

          {/* Skill Breakdown */}
          {report.skills && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold mb-4">Skill Breakdown</h2>
              <div className="space-y-4">
                {Object.entries(report.skills).map(([skill, score]) => (
                  <div key={skill}>
                    <div className="flex justify-between mb-1">
                      <span className="capitalize">{skill.replace('_', ' ')}</span>
                      <span>{score}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 rounded-full h-2 transition-all duration-500"
                        style={{ width: `${score}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent Submissions */}
          {report.recent_submissions && report.recent_submissions.length > 0 && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold mb-4">Recent Submissions</h2>
              <div className="space-y-3">
                {report.recent_submissions.map((submission, idx) => (
                  <div key={idx} className="border-b pb-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-semibold">{submission.lesson_title}</p>
                        <p className="text-sm text-gray-600">{new Date(submission.submitted_at).toLocaleDateString()}</p>
                      </div>
                      <div className="text-right">
                        <span className="inline-block px-2 py-1 bg-green-100 text-green-800 rounded text-sm">
                          Score: {submission.score}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Download Options */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4">Download Report</h2>
            <div className="flex space-x-4">
              <button
                onClick={() => handleDownload('pdf')}
                disabled={downloading}
                className="flex-1 bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 disabled:bg-gray-400 transition-colors"
              >
                {downloading ? 'Downloading...' : 'Download as PDF'}
              </button>
              <button
                onClick={() => handleDownload('csv')}
                disabled={downloading}
                className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors"
              >
                {downloading ? 'Downloading...' : 'Download as CSV'}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default MasteryReport;