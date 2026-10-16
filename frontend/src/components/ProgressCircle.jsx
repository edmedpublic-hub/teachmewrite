import React from 'react';


const ProgressCircle = ({ 
  percentage = 0, 
  size = 100, 
  strokeWidth = 8,
  label = 'Mastery',
  showLabel = true,
  primaryColor = '#2563eb',
  backgroundColor = '#e2e8f0',
  textColor = '#1e293b'
}) => {
  const radius = (size / 2) - (strokeWidth / 2);
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (Math.min(100, Math.max(0, percentage)) / 100) * circumference;
  
  // Determine color based on percentage
  const getColor = () => {
    if (percentage >= 80) return '#22c55e'; // Green
    if (percentage >= 50) return '#eab308'; // Yellow
    return '#ef4444'; // Red
  };
  
  const circleColor = primaryColor === 'auto' ? getColor() : primaryColor;

  return (
    <div className="progress-container" style={{ textAlign: 'center', padding: '10px' }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Background Circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke={backgroundColor}
          strokeWidth={strokeWidth}
        />
        {/* Progress Circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke={circleColor}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          style={{ 
            transition: 'stroke-dashoffset 0.5s ease-in-out',
            transformOrigin: 'center',
            transform: 'rotate(-90deg)'
          }}
        />
        {/* Percentage Text */}
        <text 
          x={size / 2} 
          y={size / 2 + (size * 0.05)} 
          textAnchor="middle" 
          fontSize={size * 0.16} 
          fontWeight="bold" 
          fill={textColor}
        >
          {Math.round(percentage)}%
        </text>
      </svg>
      {showLabel && (
        <div style={{ fontSize: `${size * 0.075}rem`, color: '#64748b', marginTop: '5px' }}>
          {label}
        </div>
      )}
    </div>
  );
};

export default ProgressCircle;