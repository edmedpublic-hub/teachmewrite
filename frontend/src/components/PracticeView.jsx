import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { adaptiveAPI, handleApiError } from '../services/api';
import { 
  ChevronRight, 
  CheckCircle2, 
  AlertCircle, 
  Timer, 
  Layout, 
  Send,
  LogOut
} from 'lucide-react'; // Standard icon library

// --- Sub-Components for Clarity ---

const FeedbackSection = ({ explanation }) => (
  <div className="mt-6 p-4 bg-emerald-50 border border-emerald-200 rounded-xl animate-in fade-in slide-in-from-top-2">
    <div className="flex items-start gap-3">
      <CheckCircle2 className="w-5 h-5 text-emerald-600 mt-0.5" />
      <div>
        <p className="text-emerald-800 font-bold text-sm uppercase tracking-wide">Explanation</p>
        <p className="text-emerald-700 mt-1 leading-relaxed">{explanation}</p>
      </div>
    </div>
  </div>
);

const ProgressBar = ({ current, total, isAnswered }) => {
  const percentage = Math.round(((current + (isAnswered ? 1 : 0)) / total) * 100);
  return (
    <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
      <div 
        className="bg-indigo-600 h-full transition-all duration-500 ease-out"
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
};

// --- Main Component ---

const PracticeView = () => {
  const { lessonUnitId } = useParams();
  const navigate = useNavigate();

  // State Management
  const [gameState, setGameState] = useState({
    loading: true,
    submitting: false,
    error: null,
    questions: [],
    currentIndex: 0,
    answers: {},
    currentAnswer: '',
    isAnswered: false,
    result: null,
    session: null
  });

  const [timeSpent, setTimeSpent] = useState(0);

  // Constants
  const currentQuestion = gameState.questions[gameState.currentIndex];
  const isLastQuestion = gameState.currentIndex === gameState.questions.length - 1;
  const progressPercent = useMemo(() => 
    Math.round(((gameState.currentIndex) / gameState.questions.length) * 100), 
    [gameState.currentIndex, gameState.questions.length]
  );

  useEffect(() => {
    loadData();
    const timer = setInterval(() => setTimeSpent(p => p + 1), 1000);
    return () => clearInterval(timer);
  }, [lessonUnitId]);

  const loadData = async () => {
    try {
      const data = await adaptiveAPI.getPracticeQuestions(lessonUnitId, 5);
      setGameState(prev => ({
        ...prev,
        questions: data.questions || [],
        session: {
          attempt: data.attempt_number,
          max: data.max_attempts,
          focus: data.weak_concepts || []
        },
        loading: false
      }));
    } catch (err) {
      const handled = handleApiError(err);
      setGameState(prev => ({ ...prev, error: handled.message, loading: false }));
    }
  };

  const handleNext = () => {
    if (isLastQuestion) {
      // Logic for auto-submit or final review could go here
    } else {
      setGameState(prev => ({
        ...prev,
        currentIndex: prev.currentIndex + 1,
        currentAnswer: '',
        isAnswered: false
      }));
    }
  };

  const checkAnswer = () => {
    if (!gameState.currentAnswer.trim()) return;
    
    setGameState(prev => ({
      ...prev,
      isAnswered: true,
      answers: { ...prev.answers, [currentQuestion.id]: prev.currentAnswer }
    }));
  };

  const finishSession = async () => {
    setGameState(prev => ({ ...prev, submitting: true }));
    try {
      const response = await adaptiveAPI.submitPractice(lessonUnitId, gameState.answers, timeSpent);
      setGameState(prev => ({ ...prev, result: response, submitting: false }));
    } catch (err) {
      const handled = handleApiError(err);
      setGameState(prev => ({ ...prev, error: handled.message, submitting: false }));
    }
  };

  // UI Helpers
  const formatTime = (s) => `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, '0')}`;

  if (gameState.loading) return <LoadingState />;
  if (gameState.error) return <ErrorState message={gameState.error} onRetry={loadData} />;
  if (gameState.result) return <ResultCard result={gameState.result} unitId={lessonUnitId} />;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6 min-h-screen">
      
      {/* Top Navigation / Stats */}
      <header className="flex justify-between items-center bg-white p-4 rounded-2xl shadow-sm border border-slate-100">
        <div className="flex items-center gap-4">
          <div className="bg-indigo-50 p-2 rounded-lg text-indigo-600">
            <Layout size={20} />
          </div>
          <div>
            <h1 className="font-bold text-slate-800">Mastery Practice</h1>
            <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">
              Unit ID: {lessonUnitId}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-6">
          <div className="hidden md:flex items-center gap-2 text-slate-600">
            <Timer size={18} className="text-slate-400" />
            <span className="font-mono font-bold">{formatTime(timeSpent)}</span>
          </div>
          <button 
            onClick={() => window.confirm('Exit?') && navigate('/learn')}
            className="p-2 hover:bg-red-50 text-slate-400 hover:text-red-500 transition-colors rounded-full"
          >
            <LogOut size={20} />
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Question */}
        <div className="lg:col-span-2 space-y-6">
          <section className="bg-white rounded-3xl shadow-xl shadow-slate-200/60 border border-slate-100 overflow-hidden">
            <div className="p-8">
              <div className="flex justify-between items-start mb-6">
                <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-xs font-bold uppercase tracking-tighter">
                  {currentQuestion?.type}
                </span>
                <span className="text-slate-400 text-sm font-medium">
                  Question {gameState.currentIndex + 1} of {gameState.questions.length}
                </span>
              </div>

              <h2 className="text-2xl font-semibold text-slate-800 leading-snug mb-8">
                {currentQuestion?.question}
              </h2>

              <div className="space-y-4">
                {renderInput(
                  currentQuestion, 
                  gameState.currentAnswer, 
                  (val) => setGameState(p => ({...p, currentAnswer: val})), 
                  gameState.isAnswered
                )}
              </div>

              {gameState.isAnswered && <FeedbackSection explanation={currentQuestion?.explanation} />}
            </div>

            {/* Footer Actions */}
            <div className="bg-slate-50 p-6 flex justify-between items-center border-t border-slate-100">
              {!gameState.isAnswered ? (
                <button
                  onClick={checkAnswer}
                  disabled={!gameState.currentAnswer}
                  className="w-full md:w-auto px-10 py-4 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-700 disabled:bg-slate-300 transition-all shadow-lg shadow-indigo-200 flex items-center justify-center gap-2"
                >
                  Check Answer <ChevronRight size={18} />
                </button>
              ) : (
                <div className="flex w-full gap-4">
                  {!isLastQuestion ? (
                    <button
                      onClick={handleNext}
                      className="flex-1 px-10 py-4 bg-emerad-600 text-white rounded-xl font-bold hover:bg-slate-900 transition-all flex items-center justify-center gap-2"
                    >
                      Next Question <ChevronRight size={18} />
                    </button>
                  ) : (
                    <button
                      onClick={finishSession}
                      className="flex-1 px-10 py-4 bg-violet-600 text-white rounded-xl font-bold hover:bg-emerald-700 transition-all flex items-center justify-center gap-2 shadow-lg shadow-emerald-100"
                    >
                      Finish Practice <Send size={18} />
                    </button>
                  )}
                </div>
              )}
            </div>
          </section>
        </div>

        {/* Right Column: Progress & Sidebar */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
            <h3 className="font-bold text-slate-800 mb-4">Session Progress</h3>
            <ProgressBar 
              current={gameState.currentIndex} 
              total={gameState.questions.length} 
              isAnswered={gameState.isAnswered} 
            />
            <div className="mt-4 flex justify-between text-sm">
              <span className="text-slate-500">Completion</span>
              <span className="font-bold text-indigo-600">{progressPercent}%</span>
            </div>
          </div>

          {gameState.session && (
            <div className="bg-gradient-to-br from-indigo-600 to-violet-700 p-6 rounded-3xl text-white shadow-lg">
              <h3 className="font-bold mb-2">Learning Insight</h3>
              <p className="text-indigo-100 text-sm mb-4">
                Attempt {gameState.session.attempt} of {gameState.session.max}. 
              </p>
              {gameState.session.focus.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs uppercase font-black text-indigo-200">Focus Areas:</p>
                  <div className="flex flex-wrap gap-2">
                    {gameState.session.focus.map(f => (
                      <span key={f} className="bg-white/20 px-2 py-1 rounded text-xs">{f}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

// --- Render Logic (Extracted for cleanliness) ---

const renderInput = (question, value, onChange, disabled) => {
  if (question.type === 'MCQ') {
    return (
      <div className="grid gap-3">
        {question.options?.map((opt) => (
          <button
            key={opt}
            disabled={disabled}
            onClick={() => onChange(opt)}
            className={`text-left p-4 rounded-xl border-2 transition-all flex justify-between items-center ${
              value === opt 
                ? 'border-indigo-600 bg-indigo-50 text-indigo-700 font-semibold' 
                : 'border-slate-100 hover:border-slate-200 text-slate-600'
            }`}
          >
            {opt}
            {value === opt && <CheckCircle2 size={18} />}
          </button>
        ))}
      </div>
    );
  }

  return (
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      placeholder="Type your response here..."
      rows={4}
      className="w-full p-4 rounded-2xl border-2 border-slate-100 focus:border-indigo-500 focus:ring-0 transition-all resize-none text-slate-700 outline-none"
    />
  );
};

// --- UI States ---

const LoadingState = () => (
  <div className="flex flex-col items-center justify-center h-96 gap-4">
    <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
    <p className="text-slate-500 font-medium animate-pulse">Preparing your session...</p>
  </div>
);

const ErrorState = ({ message, onRetry }) => (
  <div className="max-w-md mx-auto mt-20 text-center space-y-6">
    <div className="bg-red-50 p-6 rounded-3xl border border-red-100">
      <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
      <h2 className="text-xl font-bold text-slate-800">Something went wrong</h2>
      <p className="text-slate-600 mt-2">{message}</p>
    </div>
    <button onClick={onRetry} className="px-8 py-3 bg-slate-800 text-white rounded-xl font-bold">Try Again</button>
  </div>
);

const ResultCard = ({ result, unitId }) => {
  const navigate = useNavigate();
  return (
    <div className="max-w-2xl mx-auto mt-12 bg-white rounded-[2rem] shadow-2xl overflow-hidden border border-slate-100">
      <div className="bg-indigo-600 p-12 text-center text-white">
        <h2 className="text-3xl font-black mb-2">Practice Complete!</h2>
        <div className="text-7xl font-black mt-4">{result.score}%</div>
      </div>
      <div className="p-10 text-center">
        <p className="text-xl text-slate-600 mb-8 leading-relaxed italic">
          "{result.feedback?.message || result.feedback}"
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          {result.can_take_test ? (
            <button 
              onClick={() => navigate(`/test/${unitId}`)}
              className="px-10 py-4 bg-emerald-600 text-white rounded-2xl font-bold shadow-lg shadow-emerald-100 hover:scale-105 transition-transform"
            >
              Take Mastery Test →
            </button>
          ) : (
            <button 
              onClick={() => navigate('/learn')}
              className="px-10 py-4 bg-slate-800 text-white rounded-2xl font-bold hover:bg-slate-900 transition-colors"
            >
              Back to Lessons
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default PracticeView;