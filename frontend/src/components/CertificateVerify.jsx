// src/components/CertificateVerify.jsx
import React, { useState } from 'react';
import { certificatesAPI, handleApiError } from '../services/api';

const CertificateVerify = () => {
  const [certificateId, setCertificateId] = useState('');
  const [verificationResult, setVerificationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleVerify = async () => {
    if (!certificateId.trim()) {
      setError('Please enter a certificate ID');
      return;
    }

    setLoading(true);
    setError(null);
    setVerificationResult(null);

    try {
      const result = await certificatesAPI.verifyCertificate(certificateId);
      setVerificationResult(result);
    } catch (error) {
      const handledError = handleApiError(error);
      setError(handledError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="bg-gradient-to-r from-green-600 to-teal-600 rounded-lg shadow-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">Verify Certificate</h1>
        <p className="text-green-100">Verify the authenticity of a TeachMeWrite certificate</p>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Certificate ID
            </label>
            <input
              type="text"
              value={certificateId}
              onChange={(e) => setCertificateId(e.target.value)}
              placeholder="Enter certificate ID"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <button
            onClick={handleVerify}
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
          >
            {loading ? 'Verifying...' : 'Verify Certificate'}
          </button>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {verificationResult && (
            <div className={`p-4 rounded-lg ${verificationResult.valid ? 'bg-green-100 border-green-400' : 'bg-red-100 border-red-400'}`}>
              <div className="flex items-center">
                <div className="text-2xl mr-3">
                  {verificationResult.valid ? '✓' : '✗'}
                </div>
                <div>
                  <h3 className={`font-semibold ${verificationResult.valid ? 'text-green-800' : 'text-red-800'}`}>
                    {verificationResult.valid ? 'Certificate is Valid' : 'Certificate is Invalid'}
                  </h3>
                  {verificationResult.details && (
                    <p className="text-sm mt-1">{verificationResult.details}</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CertificateVerify;