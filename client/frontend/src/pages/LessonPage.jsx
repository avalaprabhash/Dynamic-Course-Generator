import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, ArrowRight, Play, RefreshCw, Loader2,
  CheckCircle
} from 'lucide-react';
import LessonContent from '../components/LessonContent';
import FeedbackPanel from '../components/FeedbackPanel';
import MasteryIndicator from '../components/MasteryIndicator';
import { getCourse, getProgress, submitFeedback, trackLessonAccess } from '../api';

function LessonPage() {
  const { courseId, lessonId } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [lesson, setLesson] = useState(null);
  const [module, setModule] = useState(null);
  const [progress, setProgress] = useState(null);
  const [lessonProgress, setLessonProgress] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [error, setError] = useState(null);
  
  // Navigation helpers
  const [prevLesson, setPrevLesson] = useState(null);
  const [nextLesson, setNextLesson] = useState(null);
  
  useEffect(() => {
    loadData();
  }, [courseId, lessonId]);
  
  const loadData = async () => {
    setIsLoading(true);
    try {
      const [courseData, progressData] = await Promise.all([
        getCourse(courseId),
        getProgress(courseId)
      ]);
      setCourse(courseData);
      setProgress(progressData);
      
      // Find current lesson and module
      let foundLesson = null;
      let foundModule = null;
      let allLessons = [];
      let moduleIndex = -1;
      let lessonIndex = -1;
      
      courseData.modules.forEach((mod, mIdx) => {
        mod.lessons.forEach((les, lIdx) => {
          allLessons.push({ lesson: les, module: mod });
          if (les.lesson_id === lessonId) {
            foundLesson = les;
            foundModule = mod;
            moduleIndex = mIdx;
            lessonIndex = lIdx;
          }
        });
      });
      
      setLesson(foundLesson);
      setModule(foundModule);
      
      // Track lesson access
      if (foundLesson && foundModule && moduleIndex >= 0 && lessonIndex >= 0) {
        try {
          await trackLessonAccess(courseId, moduleIndex, lessonIndex, lessonId);
        } catch (err) {
          console.error('Failed to track lesson access:', err);
        }
      }
      
      // Find prev/next lessons
      const currentIndex = allLessons.findIndex(
        item => item.lesson.lesson_id === lessonId
      );
      
      if (currentIndex > 0) {
        setPrevLesson(allLessons[currentIndex - 1]);
      } else {
        setPrevLesson(null);
      }
      
      if (currentIndex < allLessons.length - 1) {
        setNextLesson(allLessons[currentIndex + 1]);
      } else {
        setNextLesson(null);
      }
      
      // Get lesson progress
      if (progressData && foundModule) {
        const modProgress = progressData.modules?.find(
          m => m.module_id === foundModule.module_id
        );
        const lesProgress = modProgress?.lessons?.find(
          l => l.lesson_id === lessonId
        );
        setLessonProgress(lesProgress);
      }
      
    } catch (err) {
      setError('Failed to load lesson');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleRegenerate = async (cId, mId, lId, feedbackType, comments) => {
    setIsRegenerating(true);
    try {
      await submitFeedback(cId, mId, lId, feedbackType, comments);
      await loadData();
    } catch (err) {
      console.error('Failed to regenerate:', err);
    } finally {
      setIsRegenerating(false);
    }
  };
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="w-10 h-10 text-slate-400 animate-spin mx-auto mb-4" />
          <p className="text-slate-500">Loading lesson...</p>
        </div>
      </div>
    );
  }
  
  if (error || !lesson) {
    return (
      <div className="text-center py-12">
        <p className="text-rose-600 mb-4">{error || 'Lesson not found'}</p>
        <Link to={`/course/${courseId}`} className="text-slate-600 hover:underline">
          Return to course
        </Link>
      </div>
    );
  }
  
  return (
    <div className="animate-fade-in">
      {/* Breadcrumb */}
      <div className="mb-5">
        <Link 
          to={`/course/${courseId}`}
          className="inline-flex items-center gap-1.5 text-slate-500 hover:text-slate-700 text-sm"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to {course?.title}
        </Link>
      </div>
      
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-5">
          <LessonContent lesson={lesson} />
          
          {/* Feedback Section */}
          <FeedbackPanel
            courseId={courseId}
            moduleId={module?.module_id}
            lessonId={lessonId}
            onRegenerate={handleRegenerate}
            isRegenerating={isRegenerating}
          />
          
          {/* Navigation */}
          <div className="flex items-center justify-between pt-5 border-t border-slate-200">
            {prevLesson ? (
              <Link
                to={`/course/${courseId}/lesson/${prevLesson.lesson.lesson_id}`}
                className="flex items-center gap-2 text-slate-600 hover:text-slate-900 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                <div className="text-left">
                  <div className="text-xs text-slate-400">Previous</div>
                  <div className="font-medium text-sm truncate max-w-[180px]">
                    {prevLesson.lesson.lesson_title}
                  </div>
                </div>
              </Link>
            ) : (
              <div />
            )}
            
            {nextLesson ? (
              <Link
                to={`/course/${courseId}/lesson/${nextLesson.lesson.lesson_id}`}
                className="flex items-center gap-2 text-slate-600 hover:text-slate-900 transition-colors"
              >
                <div className="text-right">
                  <div className="text-xs text-slate-400">Next</div>
                  <div className="font-medium text-sm truncate max-w-[180px]">
                    {nextLesson.lesson.lesson_title}
                  </div>
                </div>
                <ArrowRight className="w-4 h-4" />
              </Link>
            ) : (
              <div />
            )}
          </div>
        </div>
        
        {/* Sidebar */}
        <div className="space-y-5">
          {/* Quiz Card */}
          <div className="bg-white rounded-xl p-5 border border-slate-200">
            <h3 className="font-semibold text-slate-900 mb-4">Test Your Knowledge</h3>
            
            {lessonProgress?.mastery && (
              <div className="mb-4">
                <MasteryIndicator mastery={lessonProgress.mastery} />
              </div>
            )}
            
            {lessonProgress?.quiz_attempts > 0 && (
              <div className="text-sm text-slate-500 mb-4">
                <p>Attempts: {lessonProgress.quiz_attempts}</p>
                <p>Best Score: {lessonProgress.best_score}%</p>
              </div>
            )}
            
            <Link
              to={`/course/${courseId}/lesson/${lessonId}/quiz`}
              className="flex items-center justify-center gap-2 w-full py-2.5 bg-slate-900 text-white rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors"
            >
              <Play className="w-4 h-4" />
              {lessonProgress?.quiz_attempts > 0 ? 'Retake Quiz' : 'Start Quiz'}
            </Link>
          </div>
          
          {/* Module Progress */}
          {module && (
            <div className="bg-white rounded-xl p-5 border border-slate-200">
              <h3 className="font-semibold text-slate-900 mb-3">Module Progress</h3>
              <p className="text-sm text-slate-600 mb-4">{module.module_title}</p>
              
              <div className="space-y-1">
                {module.lessons.map((les, index) => {
                  const isCompleted = progress?.modules?.find(m => m.module_id === module.module_id)
                    ?.lessons?.find(l => l.lesson_id === les.lesson_id)?.completed;
                  const isCurrent = les.lesson_id === lessonId;
                  
                  return (
                    <Link
                      key={les.lesson_id}
                      to={`/course/${courseId}/lesson/${les.lesson_id}`}
                      className={`flex items-center gap-3 p-2.5 rounded-lg transition-colors ${
                        isCurrent
                          ? 'bg-blue-50 text-blue-900 border border-blue-200'
                          : 'hover:bg-slate-50 text-slate-600'
                      }`}
                    >
                      {isCompleted ? (
                        <div className="w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
                          <CheckCircle className="w-3.5 h-3.5 text-white" />
                        </div>
                      ) : isCurrent ? (
                        <div className="w-5 h-5 rounded-full border-2 border-blue-500 bg-blue-100 flex-shrink-0" />
                      ) : (
                        <div className="w-5 h-5 rounded-full border-2 border-slate-300 flex-shrink-0" />
                      )}
                      <span className={`text-sm truncate ${isCompleted ? 'font-medium' : ''}`}>
                        {index + 1}. {les.lesson_title}
                      </span>
                    </Link>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default LessonPage;
