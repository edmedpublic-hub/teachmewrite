// src/components/Certificates.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { certificatesAPI, progressAPI, lessonsAPI, handleApiError } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Certificates = () => {
  const { user } = useAuth();
  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [eligibleTiers, setEligibleTiers] = useState([]);
  const [tierProgress, setTierProgress] = useState({});

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [certsData, progressData, lessonsData] = await Promise.all([
        certificatesAPI.getCertificates().catch(() => []),
        progressAPI.getUserProgress(),
        lessonsAPI.getAllLessons()
      ]);

      const certs = certsData.results || certsData || [];
      const progress = progressData.results || progressData || [];
      const lessons = lessonsData.results || lessonsData || [];

      setCertificates(certs);

      // Calculate which tiers are eligible for certificates
      const tiers = ['BASIC', 'INTERMEDIATE', 'ADVANCED', 'PROFESSIONAL'];
      const eligible = [];
      const progressMap = {};

      for (const tier of tiers) {
        const tierLessons = lessons.filter(l => l.tier === tier);
        const completedCount = tierLessons.filter(lesson => {
          const prog = progress.find(p => p.lesson === lesson.id);
          return prog?.is_completed;
        }).length;
        
        const percentage = tierLessons.length > 0 ? (completedCount / tierLessons.length) * 100 : 0;
        progressMap[tier] = { completed: completedCount, total: tierLessons.length, percentage };
        
        const hasCertificate = certs.some(c => c.tier === tier);
        if (percentage === 100 && !hasCertificate) {
          eligible.push(tier);
        }
      }

      setTierProgress(progressMap);
      setEligibleTiers(eligible);

    } catch (err) {
      const handled = handleApiError(err);
      setError(handled.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (tier) => {
    setGenerating(true);
    setError(null);
    try {
      const newCertificate = await certificatesAPI.generateCertificate(tier);
      setCertificates([newCertificate, ...certificates]);
      setEligibleTiers(eligibleTiers.filter(t => t !== tier));
      alert(`🎉 ${tier} certificate generated successfully!`);
    } catch (err) {
      const handled = handleApiError(err);
      setError(handled.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = async (certificateId, format = 'pdf') => {
    try {
      const blob = await certificatesAPI.downloadCertificate(certificateId, format);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `certificate_${certificateId}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert('Download failed. Please try again.');
    }
  };

  const getTierColor = (tier) => {
    const colors = {
      BASIC: 'from-blue-500 to-cyan-500',
      INTERMEDIATE: 'from-green-500 to-emerald-500',
      ADVANCED: 'from-purple-500 to-pink-500',
      PROFESSIONAL: 'from-orange-500 to-red-500'
    };
    return colors[tier] || 'from-gray-500 to-gray-600';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-yellow-500 to-orange-500 rounded-2xl shadow-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">🏆 Certificates</h1>
        <p className="text-yellow-100">Celebrate your achievements! Earn certificates by completing all lessons in a tier.</p>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Tier Progress */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold mb-4">📊 Your Tier Progress</h2>
        <div className="space-y-4">
          {Object.entries(tierProgress).map(([tier, data]) => {
            const isEligible = eligibleTiers.includes(tier);
            const hasCertificate = certificates.some(c => c.tier === tier);
            const isComplete = data.percentage === 100;
            
            return (
              <div key={tier} className="border rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <div>
                    <span className="font-semibold text-lg">{tier}</span>
                    <span className="ml-2 text-sm text-gray-500">
                      {data.completed}/{data.total} lessons completed
                    </span>
                  </div>
                  {hasCertificate ? (
                    <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                      ✓ Certificate Earned
                    </span>
                  ) : isComplete ? (
                    <span className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm">
                      Ready to Claim!
                    </span>
                  ) : (
                    <span className="px-3 py-1 bg-gray-100 text-gray-500 rounded-full text-sm">
                      {Math.round(data.percentage)}% Complete
                    </span>
                  )}
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                  <div 
                    className={`bg-gradient-to-r ${getTierColor(tier)} rounded-full h-2 transition-all duration-500`}
                    style={{ width: `${data.percentage}%` }}
                  />
                </div>
                {isEligible && !hasCertificate && (
                  <button
                    onClick={() => handleGenerate(tier)}
                    disabled={generating}
                    className="mt-2 px-4 py-2 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
                  >
                    {generating ? 'Generating...' : `🎓 Claim ${tier} Certificate`}
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Certificates Gallery */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold mb-4">🎖️ Your Certificates</h2>
        {certificates.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📜</div>
            <p className="text-gray-500">No certificates yet.</p>
            <p className="text-sm text-gray-400 mt-2">Complete all lessons in a tier to earn your first certificate!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {certificates.map((cert) => (
              <div key={cert.id} className="border rounded-xl overflow-hidden hover:shadow-xl transition-shadow">
                <div className={`bg-gradient-to-r ${getTierColor(cert.tier)} p-4 text-white text-center`}>
                  <div className="text-4xl mb-2">🏅</div>
                  <h3 className="font-bold text-lg">{cert.tier} Certificate</h3>
                  <p className="text-sm opacity-90">{user?.username}</p>
                </div>
                <div className="p-4">
                  <div className="text-sm text-gray-600 mb-2">
                    <div>Certificate #{cert.certificate_number?.slice(-8)}</div>
                    <div>Issued: {new Date(cert.issue_date).toLocaleDateString()}</div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleDownload(cert.id, 'pdf')}
                      className="flex-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                    >
                      📄 PDF
                    </button>
                    <button
                      onClick={() => handleDownload(cert.id, 'png')}
                      className="flex-1 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
                    >
                      🖼️ PNG
                    </button>
                  </div>
                  <div className="mt-3 text-center">
                    <span className="text-xs text-gray-400">
                      Verification: {cert.verification_code}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Motivational Card */}
      {certificates.length < 4 && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl shadow-lg p-6 text-center">
          <div className="text-4xl mb-3">🎯</div>
          <h3 className="text-lg font-semibold mb-2">Keep Going!</h3>
          <p className="text-gray-600">
            {4 - certificates.length} more {4 - certificates.length === 1 ? 'certificate' : 'certificates'} to collect!
          </p>
          <Link
            to="/learn"
            className="mt-3 inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Continue Learning →
          </Link>
        </div>
      )}
    </div>
  );
};

export default Certificates;