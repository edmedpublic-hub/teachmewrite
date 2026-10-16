// src/components/UnitBrowser.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adaptiveAPI, handleApiError } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const UnitBrowser = () => {
  const { user } = useAuth();
  const [units, setUnits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTier, setSelectedTier] = useState(user?.tier || 'BASIC');

  useEffect(() => {
    fetchUnits();
  }, [selectedTier]);

  const fetchUnits = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await adaptiveAPI.getAllUnits();
      const data = response.results || response;
      const unitsArray = Array.isArray(data) ? data : [];
      const filteredUnits = unitsArray.filter(unit => unit.tier === selectedTier);
      setUnits(filteredUnits);
      console.log('Units loaded:', filteredUnits);
    } catch (err) {
      const handled = handleApiError(err);
      setError(handled.message);
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const tiers = ['BASIC', 'INTERMEDIATE', 'ADVANCED', 'PROFESSIONAL'];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg shadow-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">Your Learning Journey</h1>
        <p className="text-blue-100">Master English writing step by step</p>
      </div>

      {/* Tier Selector */}
      <div className="bg-white rounded-lg shadow-lg p-4">
        <div className="flex flex-wrap gap-2">
          {tiers.map((tier) => (
            <button
              key={tier}
              onClick={() => setSelectedTier(tier)}
              className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                selectedTier === tier
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {tier}
            </button>
          ))}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>{error}</p>
          <button onClick={fetchUnits} className="mt-2 text-sm underline">Retry</button>
        </div>
      )}

      {/* Units and Lessons */}
      {units.length === 0 ? (
        <div className="bg-white rounded-lg shadow-lg p-12 text-center">
          <p className="text-gray-500">No units available for {selectedTier} tier yet.</p>
        </div>
      ) : (
        units.map((unit) => (
          <div key={unit.id} className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="bg-gray-50 px-6 py-4 border-b">
              <h2 className="text-2xl font-bold text-gray-800">{unit.title}</h2>
              <p className="text-gray-600">{unit.description}</p>
            </div>
            <div className="divide-y">
              {unit.lessons && unit.lessons.length > 0 ? (
                unit.lessons.map((lessonUnit) => {
                  // FIX: lesson is the ID directly (e.g., 37)
                  const lessonId = lessonUnit.lesson;
                  const unitId = unit.id;
                  
                  console.log('Lesson mapping:', {
                    lessonUnitId: lessonUnit.id,
                    lessonId: lessonId,
                    unitId: unitId,
                    title: lessonUnit.lesson_title
                  });
                  
                  // Only render if we have a valid lessonId
                  if (!lessonId) {
                    console.warn('Missing lesson ID for:', lessonUnit);
                    return (
                      <div key={lessonUnit.id} className="block px-6 py-4 bg-red-50">
                        <p className="text-red-500">Error: Missing lesson ID for {lessonUnit.lesson_title}</p>
                      </div>
                    );
                  }
                  
                  return (
                    <Link
                      key={lessonUnit.id}
                      to={`/learn/unit/${unitId}/lesson/${lessonId}`}
                      className="block px-6 py-4 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex justify-between items-center">
                        <div className="flex-1">
                          <h3 className="font-semibold text-lg">{lessonUnit.lesson_title}</h3>
                          <p className="text-gray-600 text-sm mt-1">
                            {lessonUnit.lesson_description?.substring(0, 100)}
                          </p>
                        </div>
                        <div className="ml-4">
                          {lessonUnit.user_progress?.status === 'COMPLETED' ? (
                            <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 rounded text-sm">
                              ✓ Completed
                            </span>
                          ) : lessonUnit.is_locked ? (
                            <span className="inline-flex items-center px-2 py-1 bg-gray-100 text-gray-500 rounded text-sm">
                              🔒 Locked
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-600 rounded text-sm">
                              Start →
                            </span>
                          )}
                        </div>
                      </div>
                    </Link>
                  );
                })
              ) : (
                <div className="px-6 py-4 text-gray-500 text-center">
                  No lessons available in this unit yet.
                </div>
              )}
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default UnitBrowser;