import React from 'react';
import { Trophy, TrendingUp, Target, AlertCircle } from 'lucide-react';

const masteryConfig = {
  'Mastery': {
    icon: Trophy,
    bgColor: 'bg-green-100',
    textColor: 'text-green-700',
    iconColor: 'text-green-500',
    borderColor: 'border-green-200',
  },
  'Proficient': {
    icon: TrendingUp,
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-700',
    iconColor: 'text-blue-500',
    borderColor: 'border-blue-200',
  },
  'Developing': {
    icon: Target,
    bgColor: 'bg-yellow-100',
    textColor: 'text-yellow-700',
    iconColor: 'text-yellow-500',
    borderColor: 'border-yellow-200',
  },
  'Beginning': {
    icon: AlertCircle,
    bgColor: 'bg-red-100',
    textColor: 'text-red-700',
    iconColor: 'text-red-500',
    borderColor: 'border-red-200',
  },
  'Not Started': {
    icon: Target,
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-600',
    iconColor: 'text-gray-400',
    borderColor: 'border-gray-200',
  },
};

function MasteryIndicator({ mastery, compact = false }) {
  const config = masteryConfig[mastery?.level] || masteryConfig['Not Started'];
  const Icon = config.icon;
  
  if (compact) {
    return (
      <div 
        className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full ${config.bgColor} ${config.textColor} border ${config.borderColor}`}
        title={mastery?.description}
      >
        <Icon className={`w-3 h-3 ${config.iconColor}`} />
        <span className="text-xs font-medium">{mastery?.level || 'Not Started'}</span>
      </div>
    );
  }
  
  return (
    <div className={`p-4 rounded-xl ${config.bgColor} border ${config.borderColor}`}>
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg bg-white`}>
          <Icon className={`w-5 h-5 ${config.iconColor}`} />
        </div>
        <div>
          <div className={`font-semibold ${config.textColor}`}>
            {mastery?.level || 'Not Started'}
          </div>
          <div className="text-sm text-gray-600">
            {mastery?.description || 'Take the quiz to start tracking progress'}
          </div>
        </div>
      </div>
      {mastery?.score > 0 && (
        <div className="mt-3">
          <div className="h-2 bg-white rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all ${config.iconColor.replace('text-', 'bg-')}`}
              style={{ width: `${mastery.score}%` }}
            />
          </div>
          <div className="text-xs text-gray-500 mt-1 text-right">
            {Math.round(mastery.score)}% mastery score
          </div>
        </div>
      )}
    </div>
  );
}

export default MasteryIndicator;
