import * as React from 'react';

const CircleIcon = ({ percentage = 0, size = 120, strokeWidth = 8, color = '#DD2E44' }) => {
  // Calculate the radius and circumference
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;

  // Calculate the stroke dash offset based on percentage
  // We want the stroke to fill clockwise, so we calculate how much to "hide"
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      style={{ transform: 'rotate(-90deg)' }} // Start from top
    >
      {/* Background circle (gray) */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="#E5E7EB"
        strokeWidth={strokeWidth}
      />

      {/* Progress circle (colored) */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeDasharray={circumference}
        strokeDashoffset={strokeDashoffset}
        strokeLinecap="round"
        style={{
          transition: 'stroke-dashoffset 0.5s ease-in-out',
        }}
      />

      {/* Percentage text in center */}
      <text
        x="50%"
        y="50%"
        textAnchor="middle"
        fontSize={size / 4}
        fill={color}
        fontWeight="bold"
        style={{ transform: 'rotate(90deg)', transformOrigin: 'center' }}
      >
        {Math.round(percentage)}%
      </text>
    </svg>
  );
};

export default CircleIcon;
