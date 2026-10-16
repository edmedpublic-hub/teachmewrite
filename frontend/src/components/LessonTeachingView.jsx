import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { adaptiveAPI, handleApiError } from '../services/api';
import { 
  BookOpen, 
  ArrowLeft, 
  PlayCircle, 
  GraduationCap, 
  Target, 
  BarChart3,
  Lightbulb
} from 'lucide-react';

const LessonTeachingView = () => {
  const { unitId, lessonId } = useParams();
  const navigate = useNavigate();
  
  const [state, setState] = useState({
    lessonUnit: null,
    loading: true,
    error: null,
    examples: []
  });

  useEffect(() => {
    if (!unitId || !lessonId) {
      setState(s => ({ ...s, error: 'Invalid lesson parameters.', loading: false }));
      return;
    }
    fetchData();
  }, [unitId, lessonId]);

  const fetchData = async () => {
    setState(s => ({ ...s, loading: true, error: null }));
    try {
      const data = await adaptiveAPI.getLessonUnit(unitId, lessonId);
      
      // Parse examples if they come as a string
      let parsedExamples = [];
      if (data.examples) {
        parsedExamples = typeof data.examples === 'string' 
          ? JSON.parse(data.examples) 
          : data.examples;
      }

      setState(s => ({
        ...s,
        lessonUnit: data,
        examples: parsedExamples,
        loading: false
      }));
    } catch (err) {
      const handled = handleApiError(err);
      setState(s => ({ ...s, error: handled.message, loading: false }));
    }
  };

  const getStatusConfig = (status) => {
    const configs = {
      COMPLETED: { color: 'bg-emerald-100 text-emerald-700', label: 'Mastered' },
      TEST: { color: 'bg-violet-100 text-violet-700', label: 'Test Ready' },
      PRACTICE: { color: 'bg-amber-100 text-amber-700', label: 'In Progress' },
      default: { color: 'bg-slate-100 text-slate-600', label: 'Not Started' }
    };
    return configs[status] || configs.default;
  };

  if (state.loading) return <LoadingSpinner />;
  if (state.error) return <ErrorDisplay message={state.error} onRetry={fetchData} />;
  if (!state.lessonUnit) return <EmptyState />;

  const { lessonUnit, examples } = state;
  const status = getStatusConfig(lessonUnit.status);

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8 animate-in fade-in duration-500">
      
      {/* --- Breadcrumb & Back --- */}
      <button 
        onClick={() => navigate('/learn')}
        className="flex items-center gap-2 text-slate-500 hover:text-indigo-600 transition-colors font-medium group"
      >
        <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
        Back to Curriculum
      </button>

      {/* --- Hero Header --- */}
      <header className="relative overflow-hidden bg-slate-900 rounded-[2rem] p-8 md:p-12 text-white shadow-2xl">
        <div className="relative z-10">
          <span className={`px-4 py-1 rounded-full text-xs font-bold uppercase tracking-widest ${status.color}`}>
            {status.label}
          </span>
          <h1 className="text-3xl md:text-5xl font-black mt-4 mb-2 tracking-tight">
            {lessonUnit.title}
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl font-medium">
            Master the fundamentals of English writing through adaptive learning.
          </p>
        </div>
        {/* Decorative Background Element */}
        <div className="absolute top-0 right-0 -mt-20 -mr-20 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl" />
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* --- Left Column: Content (The Meat) --- */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Main Teaching Content */}
          <section className="bg-white rounded-3xl p-8 md:p-10 shadow-sm border border-slate-100">
            <div className="flex items-center gap-3 mb-8 pb-4 border-b border-slate-50">
              <BookOpen className="text-indigo-600" size={28} />
              <h2 className="text-2xl font-bold text-slate-800 tracking-tight">Lesson Content</h2>
            </div>
            
            <article 
              className="prose prose-slate prose-lg max-w-none prose-headings:text-slate-900 prose-p:text-slate-600 prose-indigo"
              dangerouslySetInnerHTML={{ __html: lessonUnit.teaching_content }}
            />
          </section>

          {/* Examples Card */}
          {examples.length > 0 && (
            <section className="bg-indigo-50/50 rounded-3xl p-8 border border-indigo-100/50">
              <div className="flex items-center gap-3 mb-6">
                <Lightbulb className="text-indigo-600" size={24} />
                <h3 className="text-xl font-bold text-indigo-900">Practical Examples</h3>
              </div>
              <ul className="grid gap-4">
                {examples.map((item, idx) => (
                  <li key={idx} className="flex gap-4 p-4 bg-white rounded-2xl shadow-sm border border-indigo-100/30 text-slate-700 leading-relaxed font-medium">
                    <span className="text-indigo-400 font-bold">0{idx + 1}</span>
                    {item}
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>

        {/* --- Right Column: Progress & Actions --- */}
        <aside className="space-y-6">
          
          {/* Action Card */}
          <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/50 sticky top-8">
            <h3 className="font-bold text-slate-800 mb-6 flex items-center gap-2">
              <Target size={20} className="text-indigo-600" />
              Lesson Goals
            </h3>
            
            <div className="space-y-4 mb-8">
              <StatRow label="Practice Best" value={`${lessonUnit.progress?.practice_best_score || 0}%`} />
              <StatRow label="Test Best" value={`${lessonUnit.progress?.test_best_score || 0}%`} />
              <StatRow label="Attempts" value={lessonUnit.progress?.practice_attempts || 0} />
            </div>

            {/* Primary Action Button - High Visibility */}
<button 
  onClick={() => navigate(lessonUnit.status === 'TEST' ? `/test/${lessonUnit.id}` : `/practice/${lessonUnit.id}`)}
  className={`w-full py-5 rounded-2xl font-black text-xl transition-all shadow-2xl flex items-center justify-center gap-3 active:scale-[0.97] ${
    lessonUnit.status === 'TEST' 
      ? 'bg-violet-600 text-white hover:bg-violet-700 shadow-violet-200' 
      : 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-indigo-200'
  }`}
>
  {lessonUnit.status === 'TEST' ? (
    <>Take Mastery Test <GraduationCap size={24} /></>
  ) : (
    <>Start Practice Now <PlayCircle size={24} /></>
  )}
</button>

{/* Secondary Back Button (Optional: move this below the card or keep it subtle) */}
<button 
  onClick={() => navigate('/learn')}
  className="w-full mt-4 py-3 bg-white text-slate-600 border-2 border-slate-200 rounded-2xl font-bold hover:bg-slate-50 transition-colors flex items-center justify-center gap-2"
>
  <ArrowLeft size={18} /> Back to Units
</button>

            {/* Weak Concepts Sub-section */}
            {lessonUnit.progress?.weak_concepts?.length > 0 && (
              <div className="mt-8 pt-6 border-t border-slate-100">
                <div className="flex items-center gap-2 mb-4 text-amber-700">
                  <BarChart3 size={18} />
                  <span className="text-sm font-bold uppercase tracking-wider">Focus Areas</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {lessonUnit.progress.weak_concepts.map((c, i) => (
                    <span key={i} className="px-3 py-1 bg-amber-50 text-amber-700 rounded-lg text-xs font-bold border border-amber-100">
                      {c}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
};

// --- Helper Components ---

const StatRow = ({ label, value }) => (
  <div className="flex justify-between items-center py-2 border-b border-slate-50 last:border-0">
    <span className="text-slate-500 text-sm font-medium">{label}</span>
    <span className="text-slate-800 font-bold">{value}</span>
  </div>
);

const LoadingSpinner = () => (
  <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
    <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
    <p className="text-slate-500 font-medium animate-pulse">Loading course materials...</p>
  </div>
);

const ErrorDisplay = ({ message, onRetry }) => (
  <div className="max-w-md mx-auto mt-20 text-center p-8 bg-white rounded-3xl shadow-lg border border-red-100">
    <div className="w-16 h-16 bg-red-50 text-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
      <ArrowLeft size={32} />
    </div>
    <h2 className="text-xl font-bold text-slate-800">Connection Issue</h2>
    <p className="text-slate-500 mt-2 mb-6">{message}</p>
    <button onClick={onRetry} className="w-full py-3 bg-slate-900 text-white rounded-xl font-bold">Try Again</button>
  </div>
);

const EmptyState = () => (
  <div className="text-center py-20">
    <p className="text-slate-400">Lesson not found.</p>
  </div>
);

export default LessonTeachingView;