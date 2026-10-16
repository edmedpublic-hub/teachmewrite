import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { adaptiveAPI, handleApiError } from '../services/api';
import { 
  Trophy, 
  Timer, 
  ClipboardCheck, 
  AlertCircle, 
  ArrowRight, 
  RotateCcw,
  BookOpen,
  CheckCircle
} from 'lucide-react';

const TestView = () => {
  const { lessonUnitId } = useParams();
  const navigate = useNavigate();

  const [state, setState] = useState({
    loading: true,
    submitting: false,
    error: null,
    questions: [],
    answers: {},
    sessionData: null,
    result: null,
  });
  const [timeSpent, setTimeSpent] = useState(0);

  useEffect(() => {
    fetchQuestions();
    const timer = setInterval(() => setTimeSpent(p => p + 1), 1000);
    return () => clearInterval(timer);
  }, [lessonUnitId]);

  const fetchQuestions = async () => {
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await adaptiveAPI.getTestQuestions(lessonUnitId, 8);
      setState(s => ({
        ...s,
        questions: data.questions || [],
        sessionData: { testNumber: data.test_number, passingScore: data.passing_score },
        loading: false
      }));
    } catch (err) {
      const handled = handleApiError(err);
      setState(s => ({ ...s, error: handled.message, loading: false }));
    }
  };

  const handleAnswerChange = (qId, val) => {
    setState(s => ({ ...s, answers: { ...s.answers, [qId]: val } }));
  };

  const handleSubmit = async () => {
    const unanswered = state.questions.length - Object.keys(state.answers).length;
    if (unanswered > 0) {
      alert(`⚠️ Please complete the test. ${unanswered} questions left.`);
      return;
    }

    setState(s => ({ ...s, submitting: true }));
    try {
      const response = await adaptiveAPI.submitTest(lessonUnitId, state.answers, timeSpent);
      setState(s => ({ ...s, result: response, submitting: false }));
    } catch (err) {
      const handled = handleApiError(err);
      setState(s => ({ ...s, error: handled.message, submitting: false }));
    }
  };

  const formatTime = (s) => `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, '0')}`;

  if (state.loading) return <LoadingState />;
  if (state.error) return <ErrorState message={state.error} onRetry={fetchQuestions} />;
  if (state.result) return <TestResultCard result={state.result} unitId={lessonUnitId} onRetry={fetchQuestions} />;

  const answeredCount = Object.keys(state.answers).length;
  const totalQuestions = state.questions.length;
  const isComplete = answeredCount === totalQuestions;

  return (
    <div className="max-w-4xl mx-auto px-4 pb-20">
      
      {/* --- Sticky Header --- */}
      <div className="sticky top-4 z-30 mb-8">
        <div className="bg-slate-900 rounded-2xl shadow-2xl p-6 text-white border border-slate-700/50 backdrop-blur-md">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-xl font-black tracking-tight flex items-center gap-2">
                <ClipboardCheck className="text-violet-400" /> Mastery Assessment
              </h1>
              <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mt-1">
                Test #{state.sessionData?.testNumber} • Passing: {state.sessionData?.passingScore}%
              </p>
            </div>
            <div className="flex items-center gap-6">
              <div className="text-right hidden sm:block">
                <p className="text-[10px] text-slate-500 uppercase font-black">Time Elapsed</p>
                <div className="flex items-center gap-2 font-mono font-bold text-violet-400">
                  <Timer size={14} /> {formatTime(timeSpent)}
                </div>
              </div>
              <div className="h-10 w-[2px] bg-slate-800" />
              <div className="text-right">
                <p className="text-[10px] text-slate-500 uppercase font-black">Progress</p>
                <p className="font-bold">{answeredCount}/{totalQuestions}</p>
              </div>
            </div>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-4 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-violet-500 to-fuchsia-500 h-full transition-all duration-500"
              style={{ width: `${(answeredCount / totalQuestions) * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* --- Questions List --- */}
      <div className="space-y-8">
        {state.questions.map((q, idx) => (
          <div key={q.id} className="bg-white rounded-[2rem] p-8 shadow-sm border border-slate-100 relative overflow-hidden group">
             {/* Question Number Watermark */}
            <span className="absolute -top-2 -right-2 text-8xl font-black text-slate-50 opacity-[0.03] pointer-events-none group-hover:opacity-[0.05] transition-opacity">
              {idx + 1}
            </span>
            
            <div className="relative z-10">
              <div className="flex items-center gap-3 mb-6">
                <span className="px-3 py-1 bg-slate-100 text-slate-600 rounded-lg text-[10px] font-black uppercase tracking-tighter">
                  {q.type}
                </span>
                <div className="flex gap-0.5">
                  {[...Array(q.difficulty || 1)].map((_, i) => (
                    <div key={i} className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                  ))}
                </div>
              </div>

              <h3 className="text-xl font-bold text-slate-800 mb-8 leading-relaxed">
                {q.question}
              </h3>

              {renderInput(q, state.answers[q.id] || '', (val) => handleAnswerChange(q.id, val))}
            </div>
          </div>
        ))}
      </div>

      {/* --- Bottom Submit Section --- */}
      <div className="mt-12 flex flex-col items-center gap-6">
        <div className="text-center">
          <p className={`text-sm font-bold mb-4 ${isComplete ? 'text-emerald-600' : 'text-slate-400'}`}>
            {isComplete 
              ? "✨ All questions answered! Ready to submit?" 
              : `Finish ${totalQuestions - answeredCount} more questions to submit.`}
          </p>
          
          <button
            onClick={handleSubmit}
            disabled={state.submitting || !isComplete}
            className={`
              px-12 py-5 rounded-2xl font-black text-xl transition-all shadow-2xl flex items-center justify-center gap-3 active:scale-95
              ${isComplete && !state.submitting 
                ? 'bg-violet-600 text-white hover:bg-violet-700 shadow-violet-200' 
                : 'bg-slate-200 text-slate-400 cursor-not-allowed shadow-none'}
            `}
          >
            {state.submitting ? 'Processing...' : 'Submit Assessment'} 
            <ArrowRight size={24} />
          </button>
        </div>
      </div>
    </div>
  );
};

// --- Sub-Components ---

const renderInput = (q, val, onChange) => {
  if (q.type === 'MCQ') {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {q.options?.map((opt) => (
          <button
            key={opt}
            onClick={() => onChange(opt)}
            className={`p-4 rounded-2xl border-2 text-left transition-all flex items-center justify-between group ${
              val === opt 
                ? 'border-violet-600 bg-violet-50 text-violet-700 ring-4 ring-violet-50' 
                : 'border-slate-100 hover:border-slate-300 text-slate-600'
            }`}
          >
            <span className="font-bold">{opt}</span>
            <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${val === opt ? 'border-violet-600 bg-violet-600' : 'border-slate-300'}`}>
              {val === opt && <div className="w-2 h-2 bg-white rounded-full" />}
            </div>
          </button>
        ))}
      </div>
    );
  }

  return (
    <textarea
      value={val}
      onChange={(e) => onChange(e.target.value)}
      placeholder="Type your response here..."
      rows={3}
      className="w-full p-5 rounded-2xl border-2 border-slate-100 focus:border-violet-500 focus:ring-0 transition-all font-medium text-slate-700 bg-slate-50/50"
    />
  );
};

const TestResultCard = ({ result, unitId, onRetry }) => {
  const navigate = useNavigate();
  const passed = result.passed;

  return (
    <div className="max-w-2xl mx-auto mt-12 animate-in zoom-in duration-300 px-4">
      <div className={`rounded-[3rem] overflow-hidden shadow-2xl border-4 ${passed ? 'border-emerald-500' : 'border-amber-500'}`}>
        <div className={`p-12 text-center text-white ${passed ? 'bg-emerald-600' : 'bg-amber-600'}`}>
          {passed ? <Trophy size={64} className="mx-auto mb-6" /> : <BookOpen size={64} className="mx-auto mb-6" />}
          <h2 className="text-4xl font-black tracking-tight">{passed ? 'Mastery Achieved!' : 'Keep Practicing'}</h2>
          <div className="text-8xl font-black mt-4">{result.score}%</div>
          <p className="mt-4 font-bold opacity-80 uppercase tracking-widest text-sm">Required Score: {result.threshold}%</p>
        </div>
        
        <div className="bg-white p-10 text-center">
          <p className="text-xl text-slate-600 mb-10 leading-relaxed font-medium italic px-4">
            "{result.feedback?.message || result.feedback}"
          </p>

          <div className="flex flex-col gap-4">
            {passed ? (
              <button 
                onClick={() => navigate('/learn')}
                className="w-full py-5 bg-emerald-600 text-white rounded-2xl font-black text-xl hover:bg-emerald-700 shadow-xl shadow-emerald-100 transition-all flex items-center justify-center gap-3"
              >
                Proceed to Next Lesson <CheckCircle size={24} />
              </button>
            ) : (
              <>
                <button 
                  onClick={() => { onRetry(); window.scrollTo(0,0); }}
                  className="w-full py-5 bg-amber-600 text-white rounded-2xl font-black text-xl hover:bg-amber-700 shadow-xl shadow-amber-100 transition-all flex items-center justify-center gap-3"
                >
                  Retake Assessment <RotateCcw size={24} />
                </button>
                <button 
                  onClick={() => navigate('/learn')}
                  className="w-full py-4 text-slate-500 font-bold hover:text-slate-800 transition-colors"
                >
                  Review Lesson Material
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const LoadingState = () => (
  <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6">
    <div className="relative">
      <div className="w-20 h-20 border-8 border-slate-100 rounded-full" />
      <div className="w-20 h-20 border-8 border-violet-600 border-t-transparent rounded-full animate-spin absolute top-0" />
    </div>
    <p className="text-slate-500 font-black uppercase tracking-widest animate-pulse">Assembling Test...</p>
  </div>
);

const ErrorState = ({ message, onRetry }) => (
  <div className="max-w-md mx-auto mt-20 text-center p-10 bg-white rounded-[2.5rem] shadow-xl border border-red-100">
    <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-6" />
    <h2 className="text-2xl font-black text-slate-900">Technical Glitch</h2>
    <p className="text-slate-500 mt-3 mb-8 font-medium">{message}</p>
    <button onClick={onRetry} className="w-full py-4 bg-slate-900 text-white rounded-2xl font-bold shadow-lg">Try Again</button>
  </div>
);

export default TestView;