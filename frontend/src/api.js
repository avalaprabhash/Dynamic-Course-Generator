/**
 * API Service
 * 
 * Handles all communication with the FastAPI backend.
 * Uses the Vite proxy in development, direct URL in production.
 */

const API_BASE = 'http://localhost:8000';
const TOKEN_KEY = 'quiz_app_token';

/**
 * Get the auth token from localStorage
 */
function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Generic fetch wrapper with error handling
 */
async function fetchApi(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  // Add Authorization header if token exists
  const token = getToken();
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }
  
  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };
  
  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// ============== Auth APIs ==============

/**
 * Register a new user
 */
export async function register(email, password) {
  return fetchApi('/auth/register', {
    method: 'POST',
    body: JSON.stringify({
      email,
      password,
    }),
  });
}

/**
 * Login with email and password
 */
export async function login(email, password) {
  return fetchApi('/auth/login', {
    method: 'POST',
    body: JSON.stringify({
      email,
      password,
    }),
  });
}

/**
 * Get current user info
 */
export async function getCurrentUser() {
  return fetchApi('/auth/me');
}

// ============== Course APIs ==============

/**
 * Generate a new course
 */
export async function generateCourse(topic, durationHours, difficulty = 'Intermediate') {
  return fetchApi('/generate-course', {
    method: 'POST',
    body: JSON.stringify({
      topic,
      duration_hours: durationHours,
      difficulty,
    }),
  });
}


/**
 * Regenerate an existing course
 */
export async function regenerateCourse(courseId, topic, durationHours, difficulty = 'Intermediate') {
  return fetchApi('/regenerate-course', {
    method: 'POST',
    body: JSON.stringify({
      course_id: courseId,
      topic,
      duration_hours: durationHours,
      difficulty,
    }),
  });
}


/**
 * Confirm a course
 */
export async function confirmCourse(courseId) {
  return fetchApi(`/courses/${courseId}/confirm`, {
    method: 'PATCH',
  });
}


/**
 * Get list of all courses
 */
export async function getCourses() {
  return fetchApi('/courses');
}

/**
 * Get a specific course by ID
 */
export async function getCourse(courseId) {
  return fetchApi(`/courses/${courseId}`);
}

/**
 * Delete a course
 */
export async function deleteCourse(courseId) {
  return fetchApi(`/courses/${courseId}`, {
    method: 'DELETE',
  });
}

// ============== Quiz APIs ==============

/**
 * Get quiz questions for a lesson
 */
export async function getQuiz(courseId, lessonId) {
  return fetchApi(`/quiz/${courseId}/${lessonId}`);
}

/**
 * Generate a new quiz using LLM
 */
export async function generateQuiz(courseId, lessonId, difficulty = 'medium', numQuestions = 3) {
  return fetchApi('/generate-quiz', {
    method: 'POST',
    body: JSON.stringify({
      course_id: courseId,
      lesson_id: lessonId,
      difficulty,
      num_questions: numQuestions,
    }),
  });
}

/**
 * Submit quiz answers and get results
 */
export async function submitQuiz(courseId, lessonId, answers) {
  return fetchApi('/submit-quiz', {
    method: 'POST',
    body: JSON.stringify({
      course_id: courseId,
      lesson_id: lessonId,
      answers,
    }),
  });
}

/**
 * Retake a quiz with difficulty adjusted based on previous performance
 */
export async function retakeQuiz(courseId, lessonId) {
  return fetchApi('/quiz/retake', {
    method: 'POST',
    body: JSON.stringify({
      course_id: courseId,
      lesson_id: lessonId,
    }),
  });
}

/**
 * Regenerate an easier quiz when user finds it too hard
 */
export async function regenerateEasierQuiz(courseId, lessonId) {
  return fetchApi('/quiz/regenerate-easier', {
    method: 'POST',
    body: JSON.stringify({
      course_id: courseId,
      lesson_id: lessonId,
    }),
  });
}


// ============== Progress APIs ==============

/**
 * Get progress for a course
 */
export async function getProgress(courseId) {
  return fetchApi(`/progress/${courseId}`);
}

/**
 * Get progress for all courses (for resume functionality)
 */
export async function getAllProgress() {
  return fetchApi('/progress/all');
}

/**
 * Track when a user accesses a lesson (for resume functionality)
 */
export async function trackLessonAccess(courseId, moduleIndex, lessonIndex, lessonId) {
  return fetchApi('/progress/lesson-access', {
    method: 'POST',
    body: JSON.stringify({
      course_id: courseId,
      module_index: moduleIndex,
      lesson_index: lessonIndex,
      lesson_id: lessonId,
    }),
  });
}

/**
 * Mark a lesson as completed
 */
export async function markLessonCompleted(courseId, lessonId) {
  return fetchApi(`/progress/lesson-complete/${courseId}/${lessonId}`, {
    method: 'POST',
  });
}

// ============== Feedback APIs ==============

/**
 * Submit feedback and regenerate content
 */
export async function submitFeedback(courseId, moduleId, lessonId, feedbackType, comments = null) {
  return fetchApi('/feedback', {
    method: 'POST',
    body: JSON.stringify({
      course_id: courseId,
      module_id: moduleId,
      lesson_id: lessonId,
      feedback_type: feedbackType,
      additional_comments: comments,
    }),
  });
}

/**
 * Get feedback history for a course
 */
export async function getFeedbackHistory(courseId) {
  return fetchApi(`/feedback/${courseId}`);
}

// ============== Health Check ==============

/**
 * Check if the backend is running
 */
export async function healthCheck() {
  return fetchApi('/health');
}
