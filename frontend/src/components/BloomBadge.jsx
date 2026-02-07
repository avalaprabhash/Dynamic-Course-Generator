import React from 'react';

// Monochrome progression - darker = higher level
const bloomStyles = {
  Remember: { bg: 'bg-slate-100', text: 'text-slate-600', border: 'border-slate-200' },
  Understand: { bg: 'bg-slate-200', text: 'text-slate-700', border: 'border-slate-300' },
  Apply: { bg: 'bg-slate-300', text: 'text-slate-700', border: 'border-slate-400' },
  Analyze: { bg: 'bg-slate-400', text: 'text-white', border: 'border-slate-500' },
  Evaluate: { bg: 'bg-slate-500', text: 'text-white', border: 'border-slate-600' },
  Create: { bg: 'bg-slate-700', text: 'text-white', border: 'border-slate-800' },
};

const bloomDescriptions = {
  Remember: 'Recall facts and basic concepts',
  Understand: 'Explain ideas and concepts',
  Apply: 'Use information in new situations',
  Analyze: 'Draw connections among ideas',
  Evaluate: 'Justify decisions and actions',
  Create: 'Produce new or original work',
};

function BloomBadge({ level, showDescription = false, size = 'md' }) {
  const style = bloomStyles[level] || bloomStyles.Remember;
  
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-xs',
    lg: 'px-3 py-1.5 text-sm',
  };
  
  return (
    <div className="inline-flex flex-col items-start">
      <span 
        className={`inline-flex items-center font-medium rounded-md border ${style.bg} ${style.text} ${style.border} ${sizeClasses[size]}`}
        title={bloomDescriptions[level]}
      >
        {level}
      </span>
      {showDescription && (
        <span className="text-xs text-slate-500 mt-1">
          {bloomDescriptions[level]}
        </span>
      )}
    </div>
  );
}

export default BloomBadge;
