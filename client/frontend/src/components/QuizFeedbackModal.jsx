import React from 'react';
import { X, HelpCircle } from 'lucide-react';

/**
 * Feedback modal shown after a failed quiz attempt (score < 70%)
 * Allows user to indicate why they struggled
 */
function QuizFeedbackModal({ score, onFeedback, onSkip }) {
  const feedbackOptions = [
    { value: 'Too difficult', label: 'Too difficult', desc: 'Questions were above my level' },
    { value: 'Concept unclear', label: 'Concept unclear', desc: 'I need a better explanation' },
    { value: 'Need more examples', label: 'Need more examples', desc: 'More practice would help' },
    { value: 'Okay, can continue', label: 'Okay, can continue', desc: 'I understand, ready to move on' }
  ];

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-md w-full p-6 animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <HelpCircle className="w-5 h-5 text-amber-600" />
            <h3 className="text-lg font-semibold text-slate-900">
              How can we help?
            </h3>
          </div>
          <button
            onClick={onSkip}
            className="text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <p className="text-sm text-slate-600 mb-2">
          You scored <span className="font-semibold text-amber-600">{Math.round(score)}%</span> on this quiz.
        </p>
        <p className="text-sm text-slate-500 mb-4">
          Your feedback helps us adjust the difficulty for your next attempt:
        </p>

        {/* Feedback Options */}
        <div className="space-y-2 mb-4">
          {feedbackOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => onFeedback(option.value)}
              className="w-full text-left p-3 rounded-lg border border-slate-200 hover:border-blue-300 hover:bg-blue-50 transition-colors"
            >
              <div className="font-medium text-slate-900 text-sm mb-0.5">
                {option.label}
              </div>
              <div className="text-xs text-slate-500">
                {option.desc}
              </div>
            </button>
          ))}
        </div>

        {/* Skip Button */}
        <button
          onClick={onSkip}
          className="w-full text-sm text-slate-500 hover:text-slate-700 py-2"
        >
          Skip feedback
        </button>
      </div>
    </div>
  );
}

export default QuizFeedbackModal;
