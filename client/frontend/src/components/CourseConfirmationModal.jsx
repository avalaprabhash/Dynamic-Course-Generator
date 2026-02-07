import React from 'react';
import { CheckCircle, RotateCw, AlertCircle } from 'lucide-react';

function CourseConfirmationModal({ course, onConfirm, onRegenerate, isLoading }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-6 animate-fade-in">
        {/* Icon */}
        <div className="flex justify-center mb-4">
          <div className="w-14 h-14 bg-blue-100 rounded-full flex items-center justify-center">
            <AlertCircle className="w-7 h-7 text-blue-600" />
          </div>
        </div>

        {/* Title */}
        <h2 className="text-xl font-bold text-slate-900 text-center mb-2">
          Review Your Course
        </h2>

        {/* Course Info */}
        <div className="bg-slate-50 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-slate-900 mb-1">{course.title}</h3>
          <p className="text-sm text-slate-600 mb-3">{course.overview}</p>
          <div className="flex items-center gap-4 text-xs text-slate-500">
            <span>{course.duration_hours} hours</span>
            <span>•</span>
            <span>{course.modules?.length || 0} modules</span>
            <span>•</span>
            <span>
              {course.modules?.reduce((sum, m) => sum + (m.lessons?.length || 0), 0) || 0} lessons
            </span>
          </div>
        </div>

        {/* Prompt */}
        <p className="text-center text-slate-600 mb-6">
          Is this course structure okay?
        </p>

        {/* Actions */}
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={onRegenerate}
            disabled={isLoading}
            className="flex items-center justify-center gap-2 px-4 py-3 bg-slate-100 text-slate-700 rounded-lg font-medium hover:bg-slate-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RotateCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Regenerate
          </button>
          <button
            onClick={onConfirm}
            disabled={isLoading}
            className="flex items-center justify-center gap-2 px-4 py-3 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <CheckCircle className="w-4 h-4" />
            Yes, Proceed
          </button>
        </div>

        {isLoading && (
          <p className="text-center text-sm text-slate-500 mt-4">
            Regenerating course...
          </p>
        )}
      </div>
    </div>
  );
}

export default CourseConfirmationModal;
