// src/components/MyEssays.jsx
// Day 109 -- My Essays UI. Lists authenticated user's WritingFeedback rows.
// Backend endpoint: GET /api/v1/writing/essays/
// Tenant isolation: server filters by request.user; this component trusts it.
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { essaysAPI, handleApiError } from '../services/api';
import { Loader2, AlertCircle } from 'lucide-react';

const MyEssays = () => {
  const [essays, setEssays] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [numPages, setNumPages] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    let cancelled = false;
    const fetchEssays = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await essaysAPI.listEssays(page, pageSize);
        if (cancelled) return;
        setEssays(data.results || []);
        setNumPages(data.num_pages || 0);
        setTotalCount(data.count || 0);
      } catch (err) {
        if (cancelled) return;
        setError(handleApiError(err).message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    fetchEssays();
    return () => { cancelled = true; };
  }, [page, pageSize]);

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-16">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h2 className="font-semibold text-red-800">Could not load essays</h2>
            <p className="text-red-700 text-sm mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (essays.length === 0) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 text-center">
          <h1 className="text-2xl font-bold text-slate-800 mb-2">My Essays</h1>
          <p className="text-slate-500 mb-6">You have not submitted any essays yet.</p>
          <Link
            to="/studio"
            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700"
          >
            Submit your first essay
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6 flex justify-between items-baseline">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">My Essays</h1>
          <p className="text-slate-500 text-sm mt-1">
            {totalCount} essay{totalCount === 1 ? '' : 's'} submitted
          </p>
        </div>
        <Link
          to="/studio"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold text-sm hover:bg-blue-700"
        >
          + New essay
        </Link>
      </div>

      <div className="space-y-4">
        {essays.map((essay) => (
          <div
            key={essay.id}
            className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden"
          >
            <button
              onClick={() => toggleExpand(essay.id)}
              className="w-full text-left p-5 hover:bg-slate-50 transition-colors"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="text-2xl font-bold text-slate-800">
                    {essay.overall_score}
                  </span>
                  <span className="text-slate-500 text-sm">/100</span>
                  <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold">
                    {essay.tier_at_submission}
                  </span>
                  <span className="text-xs text-slate-500">Level {essay.level}</span>
                </div>
                <span className="text-xs text-slate-500">
                  {new Date(essay.created_at).toLocaleDateString()}
                </span>
              </div>
              <p className="text-slate-600 text-sm">
                {essay.student_text.length > 100
                  ? essay.student_text.slice(0, 100) + '...'
                  : essay.student_text}
              </p>
              <span className="text-blue-600 text-xs font-semibold mt-2 inline-block">
                {expandedId === essay.id ? 'Hide feedback' : 'Show feedback'}
              </span>
            </button>

            {expandedId === essay.id && (
              <div className="border-t border-slate-200 bg-slate-50 p-5">
                {essay.issues && essay.issues.length > 0 ? (
                  <div className="mb-5">
                    <h3 className="font-semibold text-slate-800 mb-2">
                      Issues ({essay.issues.length})
                    </h3>
                    <ul className="space-y-3">
                      {essay.issues.map((issue, i) => (
                        <li key={i} className="bg-white rounded-lg p-3 border border-slate-200">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-semibold text-slate-700 uppercase">
                              {issue.category}
                            </span>
                            <span className="text-xs text-slate-500">({issue.severity})</span>
                          </div>
                          <p className="text-sm text-slate-600 mb-1">{issue.explanation}</p>
                          {issue.example && (
                            <p className="text-xs text-slate-500 italic">{issue.example}</p>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : (
                  <p className="text-sm text-green-700 mb-5">
                    No issues found -- excellent writing!
                  </p>
                )}

                <div>
                  <h3 className="font-semibold text-slate-800 mb-2">Suggested rewrite</h3>
                  <p className="text-sm text-slate-600 bg-white rounded-lg p-3 border border-slate-200">
                    {essay.rewrite_suggestion}
                  </p>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {numPages > 1 && (
        <div className="mt-6 flex items-center justify-between bg-white rounded-xl border border-slate-200 p-4">
          <button
            onClick={() => setPage(page - 1)}
            disabled={page <= 1}
            className="px-4 py-2 rounded-lg font-semibold text-sm bg-slate-100 disabled:opacity-40 hover:bg-slate-200"
          >
            Previous
          </button>
          <span className="text-sm text-slate-600">
            Page {page} of {numPages}
          </span>
          <button
            onClick={() => setPage(page + 1)}
            disabled={page >= numPages}
            className="px-4 py-2 rounded-lg font-semibold text-sm bg-slate-100 disabled:opacity-40 hover:bg-slate-200"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default MyEssays;
