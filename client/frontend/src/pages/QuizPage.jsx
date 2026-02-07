import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, CheckCircle, XCircle, Loader2, 
  ChevronRight, ChevronLeft, Trophy, RefreshCw, ArrowRight,
  HelpCircle, AlertTriangle, BookOpen
} from 'lucide-react';
import BloomBadge from '../components/BloomBadge';
import DifficultyBadge from '../components/DifficultyBadge';
import { getQuiz, submitQuiz, getCourse, markLessonCompleted, retakeQuiz, regenerateEasierQuiz } from '../api';

function QuizPage() {
  const { courseId, lessonId } = useParams();
  const navigate = useNavigate();
  
  // Data state
  const [quiz, setQuiz] = useState(null);
  const [course, setCourse] = useState(null);
  const [lesson, setLesson] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Quiz interaction state
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [showExplanations, setShowExplanations] = useState({});
  
  // Feedback state
  const [showFeedbackPrompt, setShowFeedbackPrompt] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);
  
  // Retake state
  const [isRetaking, setIsRetaking] = useState(false);

  useEffect(() => {
    loadQuiz();
  }, [courseId, lessonId]);

  const loadQuiz = async () => {
    setIsLoading(true);
    setError(null);
    resetQuizState();
    
    try {
      const [quizData, courseData] = await Promise.all([
        getQuiz(courseId, lessonId),
        getCourse(courseId)
      ]);
      
      setQuiz(quizData);
      setCourse(courseData);
      
      // Find lesson info
      for (const mod of courseData.modules) {
        for (const les of mod.lessons) {
          if (les.lesson_id === lessonId) {
            setLesson(les);
            break;
          }
        }
      }
    } catch (err) {
      setError('Failed to load quiz. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const resetQuizState = () => {
    setResult(null);
    setAnswers({});
    setCurrentQuestion(0);
    setShowExplanations({});
    setShowFeedbackPrompt(true);
  };

  const handleSelectAnswer = (questionId, answer) => {
    if (result) return; // Can't change after submission
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const resultData = await submitQuiz(courseId, lessonId, answers);
      setResult(resultData);
      
      // Mark lesson completed if passed
      if (resultData.passed) {
        try {
          await markLessonCompleted(courseId, lessonId);
        } catch (err) {
          console.error('Failed to mark lesson completed:', err);
        }
      }
    } catch (err) {
      console.error('Failed to submit quiz:', err);
      setError('Failed to submit quiz. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRetake = async () => {
    setIsRetaking(true);
    resetQuizState();
    
    try {
      const quizData = await retakeQuiz(courseId, lessonId);
      setQuiz(quizData);
    } catch (err) {
      console.error('Failed to retake quiz:', err);
      // Fallback to regular quiz
      await loadQuiz();
    } finally {
      setIsRetaking(false);
    }
  };

  const handleRegenerateEasier = async () => {
    setIsRegenerating(true);
    resetQuizState();
    
    try {
      const quizData = await regenerateEasierQuiz(courseId, lessonId);
      setQuiz(quizData);
    } catch (err) {
      console.error('Failed to regenerate easier quiz:', err);
      setError('Failed to generate easier quiz. Please try again.');
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleShowExplanations = () => {
    // Show all explanations for wrong answers
    const wrongQuestions = result.feedback.filter(fb => !fb.is_correct);
    const explanationsToShow = {};
    wrongQuestions.forEach(fb => {
      explanationsToShow[fb.question_id] = true;
    });
    setShowExplanations(explanationsToShow);
    setShowFeedbackPrompt(false);
  };

  const toggleExplanation = (questionId) => {
    setShowExplanations(prev => ({ ...prev, [questionId]: !prev[questionId] }));
  };

  const goToQuestion = (index) => {
    setCurrentQuestion(index);
  };

  const nextQuestion = () => {
    if (currentQuestion < quiz.questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    }
  };

  const prevQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  // Loading state
  if (isLoading || isRegenerating || isRetaking) {
    return (
      <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center">
        <div className="bg-white rounded-2xl p-8 shadow-xl max-w-md mx-4 text-center">
          <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Loader2 className="w-8 h-8 text-slate-600 animate-spin" />
          </div>
          <h2 className="text-xl font-semibold text-slate-900 mb-2">
            {isRegenerating ? 'Creating Easier Quiz' : isRetaking ? 'Preparing New Quiz' : 'Loading Quiz'}
          </h2>
          <p className="text-slate-500">
            {isRegenerating 
              ? 'Generating new questions at an easier difficulty level...'
              : isRetaking 
              ? 'Preparing fresh questions for you to try again...'
              : 'Loading your quiz...'}
          </p>
          {(isRegenerating || isRetaking) && (
            <div className="mt-4 flex justify-center gap-1">
              <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
              <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
              <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Error state
  if (error || !quiz) {
    return (
      <div className="text-center py-12">
        <p className="text-rose-600 mb-4">{error || 'Quiz not found'}</p>
        <Link 
          to={`/course/${courseId}/lesson/${lessonId}`} 
          className="text-slate-600 hover:underline"
        >
          Return to lesson
        </Link>
      </div>
    );
  }

  const questions = quiz.questions;
  const totalQuestions = questions.length;
  const answeredCount = Object.keys(answers).length;
  const currentQ = questions[currentQuestion];

  // ============== RESULT VIEW ==============
  if (result) {
    const scoreColor = result.score >= 85 ? 'bg-emerald-500' : 
                       result.score >= 70 ? 'bg-blue-500' : 
                       result.score >= 50 ? 'bg-amber-500' : 'bg-rose-500';
    
    return (
      <div className="animate-fade-in max-w-3xl mx-auto">
        {/* Back link */}
        <Link 
          to={`/course/${courseId}/lesson/${lessonId}`}
          className="inline-flex items-center gap-1.5 text-slate-500 hover:text-slate-700 text-sm mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to lesson
        </Link>
        
        {/* Score Card */}
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden mb-6">
          <div className={`p-8 text-center text-white ${scoreColor}`}>
            <Trophy className="w-14 h-14 mx-auto mb-4 opacity-90" />
            <h1 className="text-2xl font-bold mb-2">
              {result.score >= 85 ? 'Excellent!' : 
               result.score >= 70 ? 'Great Job!' : 
               result.score >= 50 ? 'Good Effort!' : 'Keep Practicing!'}
            </h1>
            <p className="text-5xl font-bold mb-2">{Math.round(result.score)}%</p>
            <p className="opacity-90">
              {result.correct_count} of {result.total_questions} correct
            </p>
          </div>
          
          <div className="p-5 border-t">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-xs text-slate-500 mb-1">Difficulty</p>
                <DifficultyBadge difficulty={result.updated_difficulty} size="md" />
              </div>
              <div>
                <p className="text-xs text-slate-500 mb-1">Bloom Level</p>
                <BloomBadge level={result.next_bloom_level || result.current_bloom_level} size="sm" />
              </div>
              <div className="text-right">
                <p className="text-xs text-slate-500 mb-1">Status</p>
                <span className={`text-sm font-medium ${result.passed ? 'text-emerald-600' : 'text-amber-600'}`}>
                  {result.passed ? '✓ Passed' : 'Not Passed'}
                </span>
              </div>
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={handleRetake}
                disabled={isRetaking}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors text-sm disabled:opacity-50"
              >
                {isRetaking ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Loading...
                  </>
                ) : (
                  <>
                    <RefreshCw className="w-4 h-4" />
                    Try Again
                  </>
                )}
              </button>
              <Link
                to={`/course/${courseId}/lesson/${lessonId}`}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors text-sm"
              >
                Continue
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
        
        {/* Feedback Prompt - Show when there are wrong answers */}
        {result.needs_feedback && showFeedbackPrompt && (
          <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-xl p-5 mb-6">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0">
                <AlertTriangle className="w-5 h-5 text-amber-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-slate-900 mb-1">
                  You got {result.total_questions - result.correct_count} question{result.total_questions - result.correct_count > 1 ? 's' : ''} wrong
                </h3>
                <p className="text-sm text-slate-600 mb-4">
                  How can we help you learn better?
                </p>
                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={handleRegenerateEasier}
                    disabled={isRegenerating}
                    className="flex items-center gap-2 px-4 py-2.5 bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors text-sm font-medium disabled:opacity-50"
                  >
                    {isRegenerating ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <RefreshCw className="w-4 h-4" />
                        Quiz is too hard - Give me easier questions
                      </>
                    )}
                  </button>
                  <button
                    onClick={handleShowExplanations}
                    className="flex items-center gap-2 px-4 py-2.5 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
                  >
                    <BookOpen className="w-4 h-4" />
                    I need more explanation
                  </button>
                  <button
                    onClick={() => setShowFeedbackPrompt(false)}
                    className="px-4 py-2.5 text-slate-600 hover:text-slate-800 text-sm"
                  >
                    Skip
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Answer Review */}
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Review Your Answers</h2>
        <div className="space-y-4">
          {result.feedback.map((fb, index) => (
            <div 
              key={fb.question_id}
              className={`bg-white rounded-xl border p-5 ${
                fb.is_correct ? 'border-emerald-200' : 'border-rose-200'
              }`}
            >
              {/* Question header */}
              <div className="flex items-start gap-3 mb-4">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  fb.is_correct ? 'bg-emerald-100' : 'bg-rose-100'
                }`}>
                  {fb.is_correct ? (
                    <CheckCircle className="w-5 h-5 text-emerald-600" />
                  ) : (
                    <XCircle className="w-5 h-5 text-rose-600" />
                  )}
                </div>
                <div className="flex-1">
                  <p className="text-xs text-slate-500 mb-1">Question {index + 1}</p>
                  <p className="font-medium text-slate-900">{fb.question}</p>
                </div>
              </div>
              
              {/* Answers */}
              <div className="ml-11 space-y-2 mb-3">
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-slate-500">Your answer:</span>
                  <span className={fb.is_correct ? 'text-emerald-600 font-medium' : 'text-rose-600 font-medium'}>
                    {fb.user_answer || '(No answer)'}
                  </span>
                </div>
                {!fb.is_correct && (
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-slate-500">Correct:</span>
                    <span className="text-emerald-600 font-medium">{fb.correct_answer}</span>
                  </div>
                )}
              </div>
              
              {/* Explanation toggle */}
              <div className="ml-11">
                <button
                  onClick={() => toggleExplanation(fb.question_id)}
                  className="flex items-center gap-1.5 text-sm text-slate-600 hover:text-slate-800"
                >
                  <HelpCircle className="w-4 h-4" />
                  {showExplanations[fb.question_id] ? 'Hide explanation' : 'Show explanation'}
                </button>
                {showExplanations[fb.question_id] && (
                  <div className="mt-3 p-4 bg-blue-50 border border-blue-100 rounded-lg">
                    <div className="flex items-start gap-3">
                      <BookOpen className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="font-medium text-blue-900 mb-2">Explanation</p>
                        <p className="text-sm text-slate-700 leading-relaxed">
                          {fb.explanation}
                        </p>
                        {!fb.is_correct && (
                          <p className="text-sm text-slate-600 mt-3 leading-relaxed">
                            <strong>Why this matters:</strong> Understanding this concept is essential for mastering the topic. 
                            The correct answer ({fb.correct_answer}) is based on the core principles covered in this lesson. 
                            Review the lesson content to reinforce your understanding.
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // ============== QUIZ TAKING VIEW ==============
  return (
    <div className="animate-fade-in max-w-3xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link 
          to={`/course/${courseId}/lesson/${lessonId}`}
          className="inline-flex items-center gap-1.5 text-slate-500 hover:text-slate-700 text-sm mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to lesson
        </Link>
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-900">Quiz: {lesson?.lesson_title}</h1>
            <div className="flex items-center gap-2 mt-2">
              <BloomBadge level={quiz.current_bloom_level} size="sm" />
              <DifficultyBadge difficulty={quiz.current_difficulty} size="sm" />
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-slate-900">
              {currentQuestion + 1} / {totalQuestions}
            </p>
            <p className="text-xs text-slate-500">
              {answeredCount} answered
            </p>
          </div>
        </div>
        
        {/* Progress bar */}
        <div className="mt-4 h-2 bg-slate-200 rounded-full overflow-hidden">
          <div 
            className="h-full bg-blue-500 transition-all duration-300"
            style={{ width: `${(answeredCount / totalQuestions) * 100}%` }}
          />
        </div>
      </div>
      
      {/* Question Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 mb-6">
        {/* Question badges */}
        <div className="flex items-center gap-2 mb-4">
          <DifficultyBadge difficulty={currentQ.difficulty} size="sm" />
          <BloomBadge level={currentQ.bloom_level} size="sm" />
        </div>
        
        {/* Question text */}
        <h2 className="text-lg font-semibold text-slate-900 mb-6">
          {currentQ.question}
        </h2>
        
        {/* Options */}
        <div className="space-y-3">
          {currentQ.options.map((option, index) => {
            const isSelected = answers[currentQ.question_id] === option;
            const letter = String.fromCharCode(65 + index);
            
            return (
              <button
                key={index}
                onClick={() => handleSelectAnswer(currentQ.question_id, option)}
                className={`w-full p-4 text-left rounded-xl border-2 transition-all flex items-center gap-4 ${
                  isSelected 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                }`}
              >
                <span className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold ${
                  isSelected 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-slate-100 text-slate-600'
                }`}>
                  {letter}
                </span>
                <span className={`flex-1 ${isSelected ? 'text-slate-900 font-medium' : 'text-slate-700'}`}>
                  {option}
                </span>
                {isSelected && (
                  <CheckCircle className="w-5 h-5 text-blue-500" />
                )}
              </button>
            );
          })}
        </div>
      </div>
      
      {/* Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={prevQuestion}
          disabled={currentQuestion === 0}
          className="flex items-center gap-2 px-4 py-2.5 text-slate-600 hover:bg-slate-100 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
          Previous
        </button>
        
        {/* Question dots */}
        <div className="flex items-center gap-1.5 flex-wrap justify-center max-w-xs">
          {questions.map((q, index) => {
            const isAnswered = !!answers[q.question_id];
            const isCurrent = index === currentQuestion;
            
            return (
              <button
                key={q.question_id}
                onClick={() => goToQuestion(index)}
                className={`w-3 h-3 rounded-full transition-all ${
                  isCurrent 
                    ? 'bg-blue-500 ring-2 ring-blue-200' 
                    : isAnswered 
                      ? 'bg-emerald-500 hover:bg-emerald-600' 
                      : 'bg-slate-300 hover:bg-slate-400'
                }`}
                title={`Question ${index + 1}${isAnswered ? ' ✓' : ''}`}
              />
            );
          })}
        </div>
        
        {currentQuestion < totalQuestions - 1 ? (
          <button
            onClick={nextQuestion}
            className="flex items-center gap-2 px-4 py-2.5 text-slate-600 hover:bg-slate-100 rounded-lg text-sm transition-colors"
          >
            Next
            <ChevronRight className="w-4 h-4" />
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Submitting...
              </>
            ) : (
              <>
                Submit Quiz
                <CheckCircle className="w-4 h-4" />
              </>
            )}
          </button>
        )}
      </div>
      
      {/* Answer status indicator */}
      {answeredCount < totalQuestions && (
        <p className="text-center text-sm text-slate-400 mt-4">
          {answeredCount} of {totalQuestions} answered
        </p>
      )}
    </div>
  );
}

export default QuizPage;
