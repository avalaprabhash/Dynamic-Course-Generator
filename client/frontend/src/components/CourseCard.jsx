import React from 'react';
import { Link } from 'react-router-dom';
import { Clock, BookOpen, Trash2, ArrowRight } from 'lucide-react';

function CourseCard({ course, onDelete }) {
  const handleDelete = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this course?')) {
      onDelete(course.id);
    }
  };
  
  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden hover:border-slate-300 transition-colors group">
      <div className="p-5">
        <div className="flex justify-between items-start mb-3">
          <h3 className="text-base font-semibold text-slate-900 group-hover:text-slate-700 transition-colors line-clamp-2">
            {course.title}
          </h3>
          <button
            onClick={handleDelete}
            className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-md transition-colors"
            title="Delete course"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
        
        <p className="text-sm text-slate-500 mb-3">
          {course.topic}
        </p>
        
        <div className="flex items-center gap-4 text-sm text-slate-500 mb-4">
          <span className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            {course.duration_hours}h
          </span>
          <span className="flex items-center gap-1">
            <BookOpen className="w-4 h-4" />
            {course.module_count} modules
          </span>
        </div>
        
        <Link
          to={`/course/${course.id}`}
          className="flex items-center justify-center gap-2 w-full py-2.5 bg-slate-900 text-white rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors"
        >
          Continue Learning
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}

export default CourseCard;
