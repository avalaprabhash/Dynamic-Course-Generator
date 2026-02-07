import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Clock, BookOpen, ChevronRight, BarChart3, 
  CheckCircle, Circle, Loader2, Lock
} from 'lucide-react';
import BloomBadge from '../components/BloomBadge';
import MasteryIndicator from '../components/MasteryIndicator';
import ProgressBar from '../components/ProgressBar';
import CourseConfirmationModal from '../components/CourseConfirmationModal';
import { getCourse, getProgress, confirmCourse, regenerateCourse } from '../api';

function CoursePage() {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [progress, setProgress] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [error, setError] = useState(null);
  const [expandedModules, setExpandedModules] = useState({});
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  
  useEffect(() => {
    loadCourseData();
  }, [courseId]);
  
  const loadCourseData = async () => {
    setIsLoading(true);
    try {
      const [courseData, progressData] = await Promise.all([
        getCourse(courseId),
        getProgress(courseId)
      ]);
      setCourse(courseData);
      setProgress(progressData);
      
      // Show confirmation modal if course is not confirmed
      if (!courseData.confirmed) {
        setShowConfirmModal(true);
      }
      
      // Expand first module by default
      if (courseData.modules.length > 0) {
        setExpandedModules({ [courseData.modules[0].module_id]: true });
      }
    } catch (err) {
      setError('Failed to load course');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirm = async () => {
    try {
      await confirmCourse(courseId);
      setCourse({ ...course, confirmed: true });
      setShowConfirmModal(false);
    } catch (err) {
      setError('Failed to confirm course');
      console.error(err);
    }
  };

  const handleRegenerate = async () => {
    setIsRegenerating(true);
    try {
      const response = await regenerateCourse(
        courseId,
        course.topic,
        course.duration_hours,
        course.difficulty
      );
      if (response.success && response.course) {
        setCourse(response.course);
        setShowConfirmModal(false);
        await loadCourseData();
      } else {
        setError('Failed to regenerate course');
      }
    } catch (err) {
      setError('Failed to regenerate course');
      console.error(err);
    } finally {
      setIsRegenerating(false);
    }
  };
  
  const toggleModule = (moduleId) => {
    setExpandedModules(prev => ({
      ...prev,
      [moduleId]: !prev[moduleId]
    }));
  };
  
  const getLessonProgress = (moduleId, lessonId) => {
    if (!progress) return null;
    const module = progress.modules?.find(m => m.module_id === moduleId);
    return module?.lessons?.find(l => l.lesson_id === lessonId);
  };
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="w-10 h-10 text-slate-400 animate-spin mx-auto mb-4" />
          <p className="text-slate-500">Loading course...</p>
        </div>
      </div>
    );
  }
  
  if (error || !course) {
    return (
      <div className="text-center py-12">
        <p className="text-rose-600 mb-4">{error || 'Course not found'}</p>
        <Link to="/" className="text-slate-600 hover:underline">
          Return to home
        </Link>
      </div>
    );
  }
  
  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="mb-6">
        <Link 
          to="/"
          className="inline-flex items-center gap-1.5 text-slate-500 hover:text-slate-700 text-sm mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to courses
        </Link>
        
        <div className="bg-white rounded-xl p-5 border border-slate-200">
          <h1 className="text-xl font-bold text-slate-900 mb-2">{course.title}</h1>
          <p className="text-slate-600 text-sm mb-4">{course.overview}</p>
          
          <div className="flex flex-wrap items-center gap-4 mb-5">
            <span className="flex items-center gap-1.5 text-sm text-slate-500">
              <Clock className="w-4 h-4" />
              {course.duration_hours} hours
            </span>
            <span className="flex items-center gap-1.5 text-sm text-slate-500">
              <BookOpen className="w-4 h-4" />
              {course.modules.length} modules
            </span>
            <span className="flex items-center gap-1.5 text-sm text-slate-500">
              <CheckCircle className="w-4 h-4" />
              {course.modules.reduce((sum, m) => sum + m.lessons.length, 0)} lessons
            </span>
          </div>
          
          {/* Overall Progress */}
          {progress && (
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <ProgressBar 
                  value={progress.overall_progress} 
                  max={100}
                  size="md"
                  color="blue"
                />
              </div>
              <Link
                to={`/course/${courseId}/progress`}
                className="flex items-center gap-2 px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors text-sm"
              >
                <BarChart3 className="w-4 h-4" />
                Progress
              </Link>
            </div>
          )}
        </div>
      </div>
      
      {/* Modules */}
      <div className="space-y-3">
        {course.modules.map((module, moduleIndex) => (
          <div 
            key={module.module_id}
            className="bg-white rounded-xl border border-slate-200 overflow-hidden"
          >
            {/* Module Header */}
            <button
              onClick={() => toggleModule(module.module_id)}
              className="w-full p-4 flex items-center justify-between hover:bg-slate-50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center text-white font-semibold text-sm">
                  {moduleIndex + 1}
                </div>
                <div className="text-left">
                  <h2 className="font-medium text-slate-900">{module.module_title}</h2>
                  <p className="text-xs text-slate-500">{module.lessons.length} lessons</p>
                </div>
              </div>
              <ChevronRight 
                className={`w-5 h-5 text-slate-400 transition-transform ${
                  expandedModules[module.module_id] ? 'rotate-90' : ''
                }`}
              />
            </button>
            
            {/* Module Content */}
            {expandedModules[module.module_id] && (
              <div className="border-t border-slate-100">
                <p className="px-4 py-3 text-sm text-slate-600 bg-slate-50">
                  {module.module_description}
                </p>
                
                {/* Lessons */}
                <div className="divide-y divide-slate-100">
                  {module.lessons.map((lesson, lessonIndex) => {
                    const lessonProgress = getLessonProgress(module.module_id, lesson.lesson_id);
                    const isCompleted = progress?.completed_lessons?.includes(lesson.lesson_id);
                    const isCurrent = progress?.current_module_index === moduleIndex && 
                                     progress?.current_lesson_index === lessonIndex;
                    const isLocked = !course.confirmed;
                    
                    const LessonItem = (
                      <div className={`flex items-center gap-3 p-4 transition-colors ${
                        isLocked ? 'opacity-60' : 
                        isCurrent ? 'bg-blue-50 border-l-4 border-blue-500' : 
                        'hover:bg-slate-50 group cursor-pointer'
                      }`}>
                        {/* Completion status or lock */}
                        <div className="flex-shrink-0">
                          {isLocked ? (
                            <Lock className="w-5 h-5 text-slate-400" />
                          ) : isCompleted ? (
                            <div className="w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center">
                              <CheckCircle className="w-3.5 h-3.5 text-white" />
                            </div>
                          ) : isCurrent ? (
                            <div className="w-5 h-5 rounded-full border-2 border-blue-500 bg-blue-100" />
                          ) : (
                            <Circle className="w-5 h-5 text-slate-300 group-hover:text-slate-400" />
                          )}
                        </div>
                        
                        {/* Lesson info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className={`font-medium text-sm truncate ${
                              isCurrent ? 'text-blue-900' : isCompleted ? 'text-slate-900' : 'text-slate-700'
                            }`}>
                              {moduleIndex + 1}.{lessonIndex + 1} {lesson.lesson_title}
                            </span>
                            <BloomBadge level={lesson.bloom_level} size="sm" />
                            {isCurrent && (
                              <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                                In Progress
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-3 text-xs text-slate-500">
                            <span>{lesson.estimated_duration_minutes} min</span>
                            <span>{lesson.quiz.length} questions</span>
                            {lessonProgress?.best_score > 0 && (
                              <span className="text-emerald-600">
                                Best: {lessonProgress.best_score}%
                              </span>
                            )}
                          </div>
                        </div>
                        
                        {/* Mastery indicator */}
                        {!isLocked && lessonProgress?.mastery && (
                          <MasteryIndicator mastery={lessonProgress.mastery} compact />
                        )}
                        
                        {!isLocked && <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-slate-400" />}
                      </div>
                    );
                    
                    return isLocked ? (
                      <div key={lesson.lesson_id}>
                        {LessonItem}
                      </div>
                    ) : (
                      <Link
                        key={lesson.lesson_id}
                        to={`/course/${courseId}/lesson/${lesson.lesson_id}`}
                      >
                        {LessonItem}
                      </Link>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && course && (
        <CourseConfirmationModal
          course={course}
          onConfirm={handleConfirm}
          onRegenerate={handleRegenerate}
          isLoading={isRegenerating}
        />
      )}
    </div>
  );
}

export default CoursePage;
