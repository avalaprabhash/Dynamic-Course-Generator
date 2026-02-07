import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, AlertCircle, PlayCircle } from 'lucide-react';
import CourseGenerator from '../components/CourseGenerator';
import CourseCard from '../components/CourseCard';
import { generateCourse, getCourses, deleteCourse, healthCheck, getAllProgress } from '../api';

function HomePage() {
  const navigate = useNavigate();
  const [courses, setCourses] = useState([]);
  const [progressData, setProgressData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingCourses, setIsLoadingCourses] = useState(true);
  const [error, setError] = useState(null);
  const [backendStatus, setBackendStatus] = useState('checking');
  
  // Check backend health and load courses
  useEffect(() => {
    const init = async () => {
      try {
        await healthCheck();
        setBackendStatus('connected');
        await loadCourses();
        await loadProgress();
      } catch (err) {
        setBackendStatus('disconnected');
        setError('Cannot connect to backend. Make sure the server is running.');
      }
    };
    init();
  }, []);
  
  const loadCourses = async () => {
    setIsLoadingCourses(true);
    try {
      const data = await getCourses();
      setCourses(data);
    } catch (err) {
      console.error('Failed to load courses:', err);
    } finally {
      setIsLoadingCourses(false);
    }
  };
  
  const loadProgress = async () => {
    try {
      const data = await getAllProgress();
      setProgressData(data);
    } catch (err) {
      console.error('Failed to load progress:', err);
    }
  };
  
  const getProgressForCourse = (courseId) => {
    return progressData.find(p => p.course_id === courseId);
  };
  
  const handleContinue = (courseId) => {
    const progress = getProgressForCourse(courseId);
    if (progress) {
      navigate(`/course/${courseId}/lesson/${progress.current_module_index}/${progress.current_lesson_index}`);
    } else {
      navigate(`/course/${courseId}`);
    }
  };
  
  const handleGenerate = async (topic, duration, difficulty) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await generateCourse(topic, duration, difficulty);
      
      if (response.success && response.course) {
        navigate(`/course/${response.course.id}`);
      } else {
        setError(response.message || 'Failed to generate course');
      }
    } catch (err) {
      setError(err.message || 'Failed to generate course');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleDelete = async (courseId) => {
    try {
      await deleteCourse(courseId);
      setCourses(courses.filter(c => c.id !== courseId));
    } catch (err) {
      setError('Failed to delete course');
    }
  };
  
  return (
    <div className="animate-fade-in">
      {/* Hero Section */}
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-slate-900 mb-3">
          AI-Powered Dynamic Course and Quiz Generator Using Bloom's Taxonomy
        </h1>
        <p className="text-slate-600 max-w-xl mx-auto">
          Generate personalized courses with adaptive quizzes that adjust difficulty based on your feedback.
          Progress from basic recall to creative synthesis.
        </p>
      </div>
      
      {/* Backend Status Warning */}
      {backendStatus === 'disconnected' && (
        <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-lg flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0" />
          <div>
            <p className="text-amber-800 font-medium">Backend Not Connected</p>
            <p className="text-amber-700 text-sm">
              Start the server: <code className="bg-amber-100 px-2 py-0.5 rounded text-xs">cd backend && uvicorn main:app --reload</code>
            </p>
          </div>
        </div>
      )}
      
      {/* Error Display */}
      {error && backendStatus === 'connected' && (
        <div className="mb-6 p-4 bg-rose-50 border border-rose-200 rounded-lg flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-rose-600" />
          <p className="text-rose-700">{error}</p>
        </div>
      )}
      
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Course Generator */}
        <div>
          <CourseGenerator 
            onGenerate={handleGenerate} 
            isLoading={isLoading} 
          />
        </div>
        
        {/* Existing Courses */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <BookOpen className="w-5 h-5 text-slate-600" />
            <h2 className="text-lg font-semibold text-slate-900">Your Courses</h2>
            <span className="px-2 py-0.5 bg-slate-100 text-slate-600 rounded text-sm">
              {courses.length}
            </span>
          </div>
          
          {/* Resume Section */}
          {progressData.length > 0 && (
            <div className="mb-4 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <PlayCircle className="w-5 h-5 text-blue-600" />
                <h3 className="font-semibold text-blue-900">Continue Learning</h3>
              </div>
              <div className="space-y-2">
                {progressData.slice(0, 3).map((progress) => {
                  const course = courses.find(c => c.id === progress.course_id);
                  if (!course) return null;
                  
                  return (
                    <button
                      key={progress.course_id}
                      onClick={() => handleContinue(progress.course_id)}
                      className="w-full bg-white hover:bg-blue-50 border border-blue-200 rounded-lg p-3 text-left transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="font-medium text-slate-900 text-sm mb-1">
                            {progress.course_title}
                          </div>
                          <div className="flex items-center gap-3 text-xs text-slate-600">
                            <span>{Math.round(progress.overall_progress)}% complete</span>
                            <span>•</span>
                            <span>{progress.completed_lessons.length} lessons done</span>
                          </div>
                        </div>
                        <PlayCircle className="w-4 h-4 text-blue-600 flex-shrink-0" />
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}
          
          {isLoadingCourses ? (
            <div className="space-y-3">
              {[1, 2].map((i) => (
                <div key={i} className="bg-white rounded-xl p-5 animate-pulse border border-slate-200">
                  <div className="h-4 bg-slate-200 rounded w-3/4 mb-3" />
                  <div className="h-3 bg-slate-200 rounded w-1/2 mb-4" />
                  <div className="h-9 bg-slate-200 rounded" />
                </div>
              ))}
            </div>
          ) : courses.length === 0 ? (
            <div className="bg-white rounded-xl border border-slate-200 p-10 text-center">
              <BookOpen className="w-10 h-10 text-slate-300 mx-auto mb-3" />
              <h3 className="text-base font-medium text-slate-700 mb-1">No courses yet</h3>
              <p className="text-slate-500 text-sm">
                Generate your first course to start learning
              </p>
            </div>
          ) : (
            <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
              {courses.map((course) => (
                <CourseCard 
                  key={course.id} 
                  course={course} 
                  onDelete={handleDelete}
                />
              ))}
            </div>
          )}
        </div>
      </div>
      
      {/* Bloom's Taxonomy Info */}
      <div className="mt-12 bg-white rounded-xl p-6 border border-slate-200">
        <h2 className="text-lg font-semibold text-slate-900 mb-4 text-center">
          Bloom's Taxonomy Levels
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {[
            { level: 'Remember', desc: 'Recall facts' },
            { level: 'Understand', desc: 'Explain ideas' },
            { level: 'Apply', desc: 'Use knowledge' },
            { level: 'Analyze', desc: 'Break down info' },
            { level: 'Evaluate', desc: 'Make judgments' },
            { level: 'Create', desc: 'Produce new work' },
          ].map(({ level, desc }, idx) => (
            <div 
              key={level} 
              className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-center"
              style={{ opacity: 0.6 + (idx * 0.08) }}
            >
              <div className="font-medium text-slate-700 text-sm mb-0.5">{level}</div>
              <p className="text-xs text-slate-500">{desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default HomePage;
