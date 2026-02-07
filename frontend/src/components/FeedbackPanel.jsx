import React, { useState } from 'react';
import { MessageSquare, RefreshCw, Loader2, X } from 'lucide-react';

const feedbackOptions = [
  { type: 'too_easy', label: 'Too Easy', description: 'Content is not challenging enough', icon: '😴' },
  { type: 'too_hard', label: 'Too Hard', description: 'Content is too difficult', icon: '😰' },
  { type: 'unclear', label: 'Unclear', description: 'Explanations need improvement', icon: '🤔' },
  { type: 'more_examples', label: 'More Examples', description: 'Need additional examples', icon: '📝' },
  { type: 'different_approach', label: 'Different Approach', description: 'Try a different teaching method', icon: '🔄' },
];

function FeedbackPanel({ courseId, moduleId, lessonId, onRegenerate, isRegenerating }) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedType, setSelectedType] = useState(null);
  const [comments, setComments] = useState('');
  
  const handleSubmit = async () => {
    if (selectedType && onRegenerate) {
      await onRegenerate(courseId, moduleId, lessonId, selectedType, comments || null);
      setIsOpen(false);
      setSelectedType(null);
      setComments('');
    }
  };
  
  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
      >
        <MessageSquare className="w-4 h-4" />
        <span>Provide Feedback</span>
      </button>
    );
  }
  
  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 animate-fade-in">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Provide Feedback</h3>
          <p className="text-sm text-gray-500">Help us improve this content for you</p>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="p-1 text-gray-400 hover:text-gray-600 rounded"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
      
      {/* Feedback Options */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
        {feedbackOptions.map((option) => (
          <button
            key={option.type}
            onClick={() => setSelectedType(option.type)}
            className={`p-4 rounded-xl border-2 text-left transition-all ${
              selectedType === option.type
                ? 'border-indigo-500 bg-indigo-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="text-2xl mb-2">{option.icon}</div>
            <div className="font-medium text-gray-900">{option.label}</div>
            <div className="text-xs text-gray-500">{option.description}</div>
          </button>
        ))}
      </div>
      
      {/* Additional Comments */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Additional Comments (Optional)
        </label>
        <textarea
          value={comments}
          onChange={(e) => setComments(e.target.value)}
          placeholder="Tell us more about what you'd like to see changed..."
          className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
          rows={3}
        />
      </div>
      
      {/* Submit Button */}
      <div className="flex justify-end gap-3">
        <button
          onClick={() => setIsOpen(false)}
          className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
        >
          Cancel
        </button>
        <button
          onClick={handleSubmit}
          disabled={!selectedType || isRegenerating}
          className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg font-medium hover:from-indigo-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          {isRegenerating ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Regenerating...
            </>
          ) : (
            <>
              <RefreshCw className="w-4 h-4" />
              Regenerate Content
            </>
          )}
        </button>
      </div>
    </div>
  );
}

export default FeedbackPanel;
