import React from 'react';

const difficultyStyles = {
  easy: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  medium: 'bg-amber-50 text-amber-700 border-amber-200',
  hard: 'bg-rose-50 text-rose-700 border-rose-200',
};

const difficultyLabels = {
  easy: 'Easy',
  medium: 'Medium',
  hard: 'Hard',
};

function DifficultyBadge({ difficulty, size = 'md' }) {
  const colorClasses = difficultyStyles[difficulty] || difficultyStyles.medium;
  const label = difficultyLabels[difficulty] || 'Medium';
  
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-xs',
    lg: 'px-3 py-1 text-sm',
  };
  
  return (
    <span 
      className={`inline-flex items-center font-medium rounded-md border ${colorClasses} ${sizeClasses[size]}`}
    >
      {label}
    </span>
  );
}

export default DifficultyBadge;
