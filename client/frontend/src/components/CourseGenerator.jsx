import React, { useState } from 'react';
import { Sparkles, Clock, BookOpen, Loader2, Target } from 'lucide-react';

function CourseGenerator({ onGenerate, isLoading }) {
  const [topic, setTopic] = useState('');
  const [duration, setDuration] = useState(4);
    const [difficulty, setDifficulty] = useState('Intermediate');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (topic.trim() && difficulty && !isLoading) {
      onGenerate(topic.trim(), duration, difficulty);
    }
  };
  
  const suggestedTopics = [
    'Machine Learning Fundamentals',
    'React.js Development',
    'Data Structures & Algorithms',
    'Python Programming',
    'Web Security Basics',
    'Cloud Computing with AWS',
  ];
  
  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
      {/* Header */}
      <div className="bg-slate-900 p-5 text-white">
        <div className="flex items-center gap-2 mb-1">
          <Sparkles className="w-5 h-5 text-slate-300" />
          <h2 className="text-lg font-semibold">Generate New Course</h2>
        </div>
        <p className="text-slate-400 text-sm">
          Enter a topic and we'll create a structured course
        </p>
      </div>
      
      {/* Form */}
      <form onSubmit={handleSubmit} className="p-5">
        {/* Topic Input */}
        <div className="mb-5">
          <label className="block text-sm font-medium text-slate-700 mb-2">
            <BookOpen className="w-4 h-4 inline mr-1.5 text-slate-500" />
            Course Topic
          </label>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., Introduction to Machine Learning"
            className="w-full px-3 py-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent transition-all text-slate-900 placeholder-slate-400"
            disabled={isLoading}
            minLength={3}
            maxLength={200}
            required
          />
          
          {/* Suggested topics */}
          <div className="mt-3 flex flex-wrap gap-1.5">
            {suggestedTopics.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => setTopic(suggestion)}
                className="px-2.5 py-1 text-xs bg-slate-100 text-slate-600 rounded-md hover:bg-slate-200 transition-colors"
                disabled={isLoading}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
        
        {/* Duration Slider */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-700 mb-2">
            <Clock className="w-4 h-4 inline mr-1.5 text-slate-500" />
            Course Duration: <span className="text-slate-900 font-semibold">{duration} hours</span>
          </label>
          <input
            type="range"
            min="1"
            max="20"
            value={duration}
            onChange={(e) => setDuration(parseInt(e.target.value))}
            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-slate-900"
            disabled={isLoading}
          />
          <div className="flex justify-between text-xs text-slate-400 mt-1">
            <span>1 hour</span>
            <span>20 hours</span>
          </div>
        </div>

        {/* Difficulty Selector */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-700 mb-2">
            <Target className="w-4 h-4 inline mr-1.5 text-slate-500" />
            Difficulty Level
          </label>
          <div className="grid grid-cols-3 gap-2">
            {["Beginner", "Intermediate", "Advanced"].map((level) => (
              <button
                key={level}
                type="button"
                onClick={() => setDifficulty(level)}
                disabled={isLoading}
                className={`px-4 py-2.5 rounded-lg font-medium text-sm transition-all ${
                  difficulty === level
                    ? "bg-slate-900 text-white shadow-md"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {level}
              </button>
            ))}
          </div>
          <p className="text-xs text-slate-500 mt-2">
            {difficulty === "Beginner" && "Simple explanations with lots of examples"}
            {difficulty === "Intermediate" && "Balanced depth with practical applications"}
            {difficulty === "Advanced" && "Deep concepts, edge cases, and best practices"}
          </p>
        </div>
        
        {/* Submit Button */}
        <button
          type="submit"
          disabled={!topic.trim() || isLoading}
          className="w-full py-3 bg-slate-900 text-white rounded-lg font-medium hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Generating Course...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Generate Course
            </>
          )}
        </button>
        
        {isLoading && (
          <p className="text-center text-sm text-slate-500 mt-3">
            This may take a moment...
          </p>
        )}
      </form>
    </div>
  );
}

export default CourseGenerator;
