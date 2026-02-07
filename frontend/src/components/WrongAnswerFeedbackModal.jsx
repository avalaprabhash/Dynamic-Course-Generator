import React from 'react';
import { XCircle, HelpCircle, BookOpen, ArrowDown } from 'lucide-react';

const FEEDBACK_OPTIONS = [
  {
    id: 'Too difficult',
    label: 'Too difficult',
    description: 'Lower the complexity',
    icon: ArrowDown,
    iconBg: 'bg-rose-100',
    iconColor: 'text-rose-600',
    hoverBg: 'hover:bg-rose-50',
    hoverBorder: 'hover:border-rose-300'
  },
  {
    id: 'Concept unclear',
    label: 'Concept unclear',
    description: 'Need simpler explanation',
    icon: HelpCircle,
    iconBg: 'bg-amber-100',
    iconColor: 'text-amber-600',
    hoverBg: 'hover:bg-amber-50',
    hoverBorder: 'hover:border-amber-300'
  },
  {
    id: 'Need more examples',
    label: 'Need more examples',
    description: 'Show me more examples',
    icon: BookOpen,
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600',
    hoverBg: 'hover:bg-blue-50',
    hoverBorder: 'hover:border-blue-300'
  }
];

function WrongAnswerFeedbackModal({ question, correctAnswer, userAnswer, onFeedback, onContinue }) {
  const handleFeedbackSelect = (feedbackId) => {
    onFeedback(feedbackId);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 animate-fade-in">
      <div className="bg-white rounded-xl shadow-xl max-w-md w-full overflow-hidden">
        {/* Header - Wrong Answer Indicator */}
        <div className="bg-rose-500 px-5 py-4 text-white">
          <div className="flex items-center gap-3">
            <XCircle className="w-6 h-6" />
            <div>
              <h3 className="font-semibold">Incorrect Answer</h3>
              <p className="text-sm opacity-90">Help us adapt the quiz for you</p>
            </div>
          </div>
        </div>
        
        {/* Answer Summary */}
        <div className="px-5 py-4 border-b border-slate-100">
          <p className="text-sm text-slate-600 mb-2">
            <span className="font-medium">Your answer:</span>{' '}
            <span className="text-rose-600">{userAnswer}</span>
          </p>
          <p className="text-sm text-slate-600">
            <span className="font-medium">Correct answer:</span>{' '}
            <span className="text-emerald-600">{correctAnswer}</span>
          </p>
        </div>
        
        {/* Feedback Options */}
        <div className="p-5">
          <p className="text-sm font-medium text-slate-700 mb-3">
            What would help you learn better?
          </p>
          
          <div className="space-y-2">
            {FEEDBACK_OPTIONS.map((option) => {
              const Icon = option.icon;
              return (
                <button
                  key={option.id}
                  onClick={() => handleFeedbackSelect(option.id)}
                  className={`w-full flex items-center gap-3 p-3 rounded-lg border transition-all
                    border-slate-200 ${option.hoverBorder} ${option.hoverBg}
                    text-left group`}
                >
                  <div className={`w-9 h-9 rounded-lg ${option.iconBg} flex items-center justify-center`}>
                    <Icon className={`w-5 h-5 ${option.iconColor}`} />
                  </div>
                  <div>
                    <p className="font-medium text-slate-800 text-sm">{option.label}</p>
                    <p className="text-xs text-slate-500">{option.description}</p>
                  </div>
                </button>
              );
            })}
          </div>
          
          {/* Skip Option */}
          <button
            onClick={onContinue}
            className="w-full mt-3 py-2 text-sm text-slate-500 hover:text-slate-700 transition-colors"
          >
            Skip and continue
          </button>
        </div>
      </div>
    </div>
  );
}

export default WrongAnswerFeedbackModal;
