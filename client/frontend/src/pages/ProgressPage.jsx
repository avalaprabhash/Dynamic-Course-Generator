import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, Trophy, Target, TrendingUp, Clock,
  Loader2, CheckCircle, Circle
} from 'lucide-react';
import BloomBadge from '../components/BloomBadge';
import DifficultyBadge from '../components/DifficultyBadge';
import MasteryIndicator from '../components/MasteryIndicator';
import ProgressBar from '../components/ProgressBar';
import { getCourse, getProgress } from '../api';

function ProgressPage() {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [progress, setProgress] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    loadData();
  }, [courseId]);
  
  const loadData = async () => {
    setIsLoading(true);
    try {
      const [courseData, progressData] = await Promise.all([
        getCourse(courseId),
        getProgress(courseId)
      ]);
      setCourse(courseData);
      setProgress(progressData);
    } catch (err) {
      setError('Failed to load progress');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-indigo-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-500">Loading progress...</p>
        </div>
      </div>
    );
  }
  
  if (error || !course || !progress) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500 mb-4">{error || 'Data not found'}</p>
        <Link to={`/course/${courseId}`} className="text-indigo-600 hover:underline">
          Return to course
        </Link>
      </div>
    );
  }
  
  // Calculate statistics
  const totalLessons = course.modules.reduce((sum, m) => sum + m.lessons.length, 0);
  const completedLessons = progress.modules.reduce((sum, m) => 
    sum + m.lessons.filter(l => l.completed).length, 0
  );
  const totalQuizAttempts = progress.modules.reduce((sum, m) => 
    sum + m.lessons.reduce((lSum, l) => lSum + (l.quiz_attempts || 0), 0), 0
  );
  const avgScore = progress.modules.reduce((sum, m) => {
    const scores = m.lessons.filter(l => l.best_score > 0).map(l => l.best_score);
    return sum + scores.reduce((s, score) => s + score, 0);
  }, 0) / (completedLessons || 1);
  
  // Count mastery levels
  const masteryCount = { Mastery: 0, Proficient: 0, Developing: 0, Beginning: 0, 'Not Started': 0 };
  progress.modules.forEach(m => {
    m.lessons.forEach(l => {
      const level = l.mastery?.level || 'Not Started';
      masteryCount[level]++;
    });
  });
  
  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="mb-8">
        <Link 
          to={`/course/${courseId}`}
          className="inline-flex items-center gap-2 text-gray-500 hover:text-gray-700 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to course
        </Link>
        
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Learning Progress</h1>
        <p className="text-gray-600">{course.title}</p>
      </div>
      
      {/* Stats Cards */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-indigo-100 rounded-lg">
              <Target className="w-5 h-5 text-indigo-600" />
            </div>
            <span className="text-sm text-gray-500">Overall Progress</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {Math.round(progress.overall_progress)}%
          </p>
          <ProgressBar value={progress.overall_progress} showLabel={false} size="sm" />
        </div>
        
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <span className="text-sm text-gray-500">Completed</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {completedLessons} / {totalLessons}
          </p>
          <p className="text-sm text-gray-500">lessons completed</p>
        </div>
        
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <TrendingUp className="w-5 h-5 text-purple-600" />
            </div>
            <span className="text-sm text-gray-500">Average Score</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {Math.round(avgScore)}%
          </p>
          <p className="text-sm text-gray-500">on quizzes</p>
        </div>
        
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-amber-100 rounded-lg">
              <Trophy className="w-5 h-5 text-amber-600" />
            </div>
            <span className="text-sm text-gray-500">Quiz Attempts</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {totalQuizAttempts}
          </p>
          <p className="text-sm text-gray-500">total attempts</p>
        </div>
      </div>
      
      {/* Mastery Distribution */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Mastery Distribution</h2>
        <div className="grid grid-cols-5 gap-4">
          {Object.entries(masteryCount).map(([level, count]) => {
            const colors = {
              'Mastery': 'bg-green-500',
              'Proficient': 'bg-blue-500',
              'Developing': 'bg-yellow-500',
              'Beginning': 'bg-red-500',
              'Not Started': 'bg-gray-300'
            };
            return (
              <div key={level} className="text-center">
                <div className={`w-full h-24 ${colors[level]} rounded-lg mb-2 flex items-end justify-center pb-2`}
                  style={{ height: `${Math.max(20, (count / totalLessons) * 100)}px` }}
                >
                  <span className="text-white font-bold">{count}</span>
                </div>
                <p className="text-xs text-gray-600">{level}</p>
              </div>
            );
          })}
        </div>
      </div>
      
      {/* Detailed Progress */}
      <div className="space-y-6">
        <h2 className="text-lg font-semibold text-gray-900">Detailed Progress</h2>
        
        {course.modules.map((module, moduleIndex) => {
          const moduleProgress = progress.modules.find(m => m.module_id === module.module_id);
          
          return (
            <div key={module.module_id} className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              {/* Module Header */}
              <div className="p-4 bg-gray-50 border-b border-gray-100">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
                    {moduleIndex + 1}
                  </div>
                  <h3 className="font-semibold text-gray-900">{module.module_title}</h3>
                </div>
              </div>
              
              {/* Lessons */}
              <div className="divide-y divide-gray-100">
                {module.lessons.map((lesson, lessonIndex) => {
                  const lessonProgress = moduleProgress?.lessons?.find(
                    l => l.lesson_id === lesson.lesson_id
                  ) || { completed: false, quiz_attempts: 0, best_score: 0 };
                  
                  return (
                    <div key={lesson.lesson_id} className="p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex items-center gap-4">
                        {/* Status */}
                        <div className="flex-shrink-0">
                          {lessonProgress.completed ? (
                            <CheckCircle className="w-5 h-5 text-green-500" />
                          ) : (
                            <Circle className="w-5 h-5 text-gray-300" />
                          )}
                        </div>
                        
                        {/* Lesson Info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <Link 
                              to={`/course/${courseId}/lesson/${lesson.lesson_id}`}
                              className="font-medium text-gray-900 hover:text-indigo-600 transition-colors"
                            >
                              {moduleIndex + 1}.{lessonIndex + 1} {lesson.lesson_title}
                            </Link>
                            <BloomBadge level={lesson.bloom_level} size="sm" />
                          </div>
                          
                          <div className="flex items-center gap-4 text-sm text-gray-500">
                            <span>{lesson.estimated_duration_minutes} min</span>
                            <span>Attempts: {lessonProgress.quiz_attempts}</span>
                            {lessonProgress.best_score > 0 && (
                              <span className="text-green-600">
                                Best: {lessonProgress.best_score}%
                              </span>
                            )}
                          </div>
                        </div>
                        
                        {/* Difficulty */}
                        <DifficultyBadge 
                          difficulty={lessonProgress.current_difficulty || 'medium'} 
                          size="sm" 
                        />
                        
                        {/* Mastery */}
                        <MasteryIndicator mastery={lessonProgress.mastery} compact />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
      
      {/* Bloom's Taxonomy Progress */}
      <div className="mt-8 bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Bloom's Taxonomy Progress</h2>
        <p className="text-sm text-gray-500 mb-6">
          Track your progression through the cognitive levels of learning
        </p>
        
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create'].map(level => {
            // Count lessons at this level
            let total = 0;
            let completed = 0;
            
            course.modules.forEach(module => {
              module.lessons.forEach(lesson => {
                if (lesson.bloom_level === level) {
                  total++;
                  const moduleProgress = progress.modules.find(m => m.module_id === module.module_id);
                  const lessonProgress = moduleProgress?.lessons?.find(l => l.lesson_id === lesson.lesson_id);
                  if (lessonProgress?.completed) completed++;
                }
              });
            });
            
            const percentage = total > 0 ? (completed / total) * 100 : 0;
            
            return (
              <div key={level} className="p-4 rounded-xl border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <BloomBadge level={level} size="md" />
                  <span className="text-sm text-gray-500">{completed}/{total}</span>
                </div>
                <ProgressBar 
                  value={percentage} 
                  showLabel={false} 
                  size="sm" 
                  color={percentage === 100 ? 'green' : 'indigo'} 
                />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default ProgressPage;
