// src/components/WritingStudio.jsx
import React, { useState } from 'react';
import { aiService } from '../services/aiService';
import { Send, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

const WritingStudio = () => {
  const [text, setText] = useState('');
  const [level, setLevel] = useState(5);
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;

    setLoading(true);
    setError(null);
    setFeedback(null);

    try {
      const data = await aiService.getWritingFeedback(text, level);
      setFeedback(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-8">
        <h1 className="text-2xl font-bold text-slate-800 mb-2">AI Writing Studio</h1>
        <p className="text-slate-500 mb-6">Submit your essay to receive instant, curriculum-aligned feedback.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex items-center gap-4">
            <label className="font-semibold text-slate-700">Select Level:</label>
            <select
              value={level}
              onChange={(e) => setLevel(e.target.value)}
              className="p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              {[1, 2, 3, 4, 5, 6, 7].map(l => (
                <option key={l} value={l}>Level {l}</option>
              ))}
            </select>
          </div>

          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Type or paste your essay here..."
            className="w-full h-40 p-4 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
          />

          <button
            type="submit"
            disabled={loading || !text.trim()}
            className="w-full md:w-auto px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            {loading ? 'Analyzing...' : 'Get Feedback'}
          </button>
        </form>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3 mb-8">
          <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {feedback && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 animate-in fade-in slide-in-from-bottom-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-4">
            <h2 className="text-xl font-bold text-slate-800">Feedback Results</h2>
            <div className="px-4 py-2 bg-indigo-50 text-indigo-700 font-bold rounded-lg">
              Score: {feedback.overall_score}/100
            </div>
          </div>

          {feedback.issues.length === 0 ? (
            <div className="flex items-center gap-3 p-4 bg-emerald-50 text-emerald-700 rounded-lg">
              <CheckCircle2 className="w-6 h-6" />
              <p className="font-semibold">Excellent! No grammatical or structural issues found.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {feedback.issues.map((issue, idx) => (
                <div key={idx} className={`p-4 border rounded-xl ${
                  issue.severity === 'high' ? 'bg-red-50 border-red-100' :
                  issue.severity === 'medium' ? 'bg-amber-50 border-amber-100' :
                  'bg-slate-50 border-slate-100'
                }`}>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2 py-1 text-xs font-bold uppercase tracking-wider bg-white rounded-md border border-slate-200">
                      {issue.category}
                    </span>
                    <span className="text-sm font-semibold opacity-75">({issue.severity} severity)</span>
                  </div>
                  <p className="font-medium text-slate-800 mb-2">{issue.explanation}</p>
                  <p className="text-sm italic text-slate-600 bg-white p-2 rounded border border-slate-100">"{issue.example}"</p>
                </div>
              ))}
            </div>
          )}

          <div className="mt-6 p-4 bg-indigo-50 border border-indigo-100 rounded-xl">
            <h3 className="font-bold text-indigo-900 mb-2">Suggested Rewrite:</h3>
            <p className="text-indigo-800">{feedback.rewrite_suggestion}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default WritingStudio;
