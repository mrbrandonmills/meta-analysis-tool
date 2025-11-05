import React from 'react';
import { formatDuration } from '@/lib/utils';

interface ProgressIndicatorProps {
  progress: number; // 0-100
  label?: string;
  eta?: number; // seconds
  variant?: 'bar' | 'circular' | 'dots';
  size?: 'sm' | 'md' | 'lg';
  color?: 'blue' | 'green' | 'purple' | 'indigo';
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  progress,
  label,
  eta,
  variant = 'bar',
  size = 'md',
  color = 'blue'
}) => {
  const colorClasses = {
    blue: 'bg-blue-600',
    green: 'bg-green-600',
    purple: 'bg-purple-600',
    indigo: 'bg-indigo-600'
  };

  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  };

  if (variant === 'bar') {
    return (
      <div className="w-full">
        {(label || eta) && (
          <div className="flex justify-between items-center mb-2">
            {label && <span className="text-sm font-medium text-gray-700">{label}</span>}
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              {progress !== undefined && <span>{Math.round(progress)}%</span>}
              {eta && <span className="text-gray-500">• ETA {formatDuration(eta)}</span>}
            </div>
          </div>
        )}
        <div className={`w-full bg-gray-200 rounded-full overflow-hidden ${sizeClasses[size]}`}>
          <div
            className={`${colorClasses[color]} ${sizeClasses[size]} rounded-full transition-all duration-300 ease-out`}
            style={{ width: `${Math.min(Math.max(progress, 0), 100)}%` }}
          />
        </div>
      </div>
    );
  }

  if (variant === 'circular') {
    const radius = size === 'sm' ? 20 : size === 'md' ? 30 : 40;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (progress / 100) * circumference;

    return (
      <div className="flex flex-col items-center">
        <div className="relative">
          <svg
            className="transform -rotate-90"
            width={radius * 2 + 10}
            height={radius * 2 + 10}
          >
            {/* Background circle */}
            <circle
              cx={radius + 5}
              cy={radius + 5}
              r={radius}
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="3"
            />
            {/* Progress circle */}
            <circle
              cx={radius + 5}
              cy={radius + 5}
              r={radius}
              fill="none"
              stroke="currentColor"
              strokeWidth="3"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              className={`text-${color}-600 transition-all duration-300`}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-sm font-semibold text-gray-700">
              {Math.round(progress)}%
            </span>
          </div>
        </div>
        {label && <p className="mt-2 text-sm text-gray-600">{label}</p>}
        {eta && <p className="text-xs text-gray-500">ETA {formatDuration(eta)}</p>}
      </div>
    );
  }

  if (variant === 'dots') {
    return (
      <div className="flex items-center space-x-2">
        {label && <span className="text-sm font-medium text-gray-700 mr-2">{label}</span>}
        <div className="flex space-x-1">
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className={`w-2 h-2 rounded-full ${colorClasses[color]} animate-bounce`}
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </div>
      </div>
    );
  }

  return null;
};

export default ProgressIndicator;
