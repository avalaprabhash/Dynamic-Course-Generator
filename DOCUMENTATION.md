# AI-Powered Dynamic Course & Quiz Generator - Complete Technical Documentation

> **Version**: 2.0.0  
> **Last Updated**: January 30, 2026  
> **Author**: Quiz Generator Development Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Backend Documentation](#4-backend-documentation)
5. [Frontend Documentation](#5-frontend-documentation)
6. [Database Schema & Storage](#6-database-schema--storage)
7. [API Reference](#7-api-reference)
8. [Authentication System](#8-authentication-system)
9. [LLM Integration](#9-llm-integration)
10. [Bloom's Taxonomy Implementation](#10-blooms-taxonomy-implementation)
11. [Adaptive Learning Algorithms](#11-adaptive-learning-algorithms)
12. [Quiz System](#12-quiz-system)
13. [Progress Tracking](#13-progress-tracking)
14. [Configuration & Environment](#14-configuration--environment)
15. [Deployment Guide](#15-deployment-guide)
16. [Troubleshooting](#16-troubleshooting)

---

## 1. Executive Summary

### 1.1 Project Overview

The **AI-Powered Dynamic Course & Quiz Generator** is an intelligent e-learning platform that leverages artificial intelligence to create personalized educational content. The system generates structured courses based on user-specified topics and durations, incorporating Bloom's Taxonomy to ensure progressive cognitive development from basic recall to advanced creative synthesis.

### 1.2 Key Features

| Feature | Description |
|---------|-------------|
| **AI Course Generation** | Generates complete courses with modules, lessons, and quizzes using LLM (Perplexity API) |
| **Bloom's Taxonomy Alignment** | Content structured across 6 cognitive levels: Remember → Understand → Apply → Analyze → Evaluate → Create |
| **Adaptive Quiz System** | Quiz difficulty adjusts based on user performance and feedback |
| **User Authentication** | JWT-based authentication with secure password hashing (Argon2) |
| **Progress Tracking** | Comprehensive tracking of lesson completion, quiz attempts, and mastery levels |
| **Content Regeneration** | Users can request content improvements via feedback system |
| **Modern UI** | Clean, responsive React interface with TailwindCSS |

### 1.3 System Requirements

**Backend:**
- Python 3.9+
- pip (Python package manager)

**Frontend:**
- Node.js 18+
- npm or yarn

**Optional:**
- Perplexity API key for live LLM content generation

---

## 2. System Architecture

### 2.1 High-Level Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                       │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                        React Frontend (Vite)                              │  │
│  │   Port: 5173                                                              │  │
│  │   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │  │
│  │   │  Auth    │ │  Home    │ │  Course  │ │  Lesson  │ │    Quiz      │   │  │
│  │   │  Pages   │ │  Page    │ │  Page    │ │  Page    │ │    Page      │   │  │
│  │   └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │  │
│  │                           │                                               │  │
│  │                    AuthContext (JWT Token Management)                     │  │
│  │                           │                                               │  │
│  │                      api.js (HTTP Client)                                 │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTP/JSON (REST API)
                                      │ Authorization: Bearer <JWT>
                                      ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                              SERVER LAYER                                       │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                     FastAPI Backend Server                                │  │
│  │   Port: 8000                                                              │  │
│  │                                                                           │  │
│  │   ┌─────────────────────────────────────────────────────────────────┐    │  │
│  │   │                      main.py (API Router)                        │    │  │
│  │   │   /auth/*  │  /courses/*  │  /quiz/*  │  /progress/*  │  /feedback/* │  │
│  │   └─────────────────────────────────────────────────────────────────┘    │  │
│  │                    │              │              │                        │  │
│  │   ┌────────────────┼──────────────┼──────────────┼────────────────────┐  │  │
│  │   │                ▼              ▼              ▼                    │  │  │
│  │   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐    │  │  │
│  │   │  │course_        │  │quiz_service  │  │auth.py               │    │  │  │
│  │   │  │generator.py   │  │.py           │  │(JWT + Argon2)        │    │  │  │
│  │   │  └──────┬───────┘  └──────┬───────┘  └──────────────────────┘    │  │  │
│  │   │         │                 │                                       │  │  │
│  │   │         └────────┬────────┘                                       │  │  │
│  │   │                  ▼                                                 │  │  │
│  │   │    ┌──────────────────────────────────────────────────────────┐  │  │  │
│  │   │    │              llm_service.py (Perplexity API)             │  │  │  │
│  │   │    │   - Course content generation                            │  │  │  │
│  │   │    │   - Quiz question generation                             │  │  │  │
│  │   │    │   - Content regeneration based on feedback               │  │  │  │
│  │   │    └──────────────────────────────────────────────────────────┘  │  │  │
│  │   └───────────────────────────────────────────────────────────────────┘  │  │
│  │                                      │                                    │  │
│  │                                      ▼                                    │  │
│  │   ┌──────────────────────────────────────────────────────────────────┐   │  │
│  │   │                    storage.py (JSON Persistence)                  │   │  │
│  │   └──────────────────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                         │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                      JSON File Storage (backend/data/)                    │  │
│  │                                                                           │  │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │  │
│  │   │  courses/    │  │  progress/   │  │  feedback/   │  │  users.json │  │  │
│  │   │  {id}.json   │  │  {id}_{user} │  │  {id}_       │  │             │  │  │
│  │   │              │  │  .json       │  │  feedback    │  │             │  │  │
│  │   │              │  │              │  │  .json       │  │             │  │  │
│  │   └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘  │  │
│  │                                                                           │  │
│  │   ┌──────────────┐  ┌──────────────┐                                     │  │
│  │   │  versions/   │  │ quiz_memory/ │                                     │  │
│  │   │  (history)   │  │ (attempt     │                                     │  │
│  │   │              │  │  tracking)   │                                     │  │
│  │   └──────────────┘  └──────────────┘                                     │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ API Calls
                                      ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL SERVICES                                     │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                    Perplexity AI API (sonar model)                        │  │
│  │                    https://api.perplexity.ai                              │  │
│  │                                                                           │  │
│  │   Used for:                                                               │  │
│  │   - Generating course structure and content                               │  │
│  │   - Creating quiz questions aligned with Bloom's Taxonomy                 │  │
│  │   - Regenerating content based on user feedback                          │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Request Flow

```
User Action → React Component → api.js → FastAPI Endpoint → Service Layer → Storage/LLM → Response
```

**Example: Generating a Course**
```
1. User fills CourseGenerator form (topic: "Python", duration: 4 hours)
2. HomePage calls generateCourse() from api.js
3. api.js sends POST /generate-course with JWT token
4. FastAPI validates JWT via get_current_user dependency
5. course_generator.py calls llm_service.generate_course_content()
6. llm_service.py sends prompt to Perplexity API
7. Response is validated and structured into Course model
8. storage.py saves course to data/courses/{id}.json
9. Response sent back through chain to frontend
10. User navigated to CoursePage
```

---

## 3. Technology Stack

### 3.1 Backend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.9+ | Core programming language |
| **FastAPI** | 0.109.0 | High-performance async web framework |
| **Uvicorn** | 0.27.0 | ASGI server |
| **Pydantic** | 2.5.3 | Data validation and serialization |
| **OpenAI SDK** | 1.12.0 | LLM API client (configured for Perplexity) |
| **python-jose** | 3.3.0 | JWT token handling |
| **argon2-cffi** | 23.1.0 | Password hashing |
| **httpx** | 0.26.0 | Async HTTP client |
| **python-dotenv** | 1.0.0 | Environment variable management |

### 3.2 Frontend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.2.0 | UI library |
| **Vite** | 5.0.8 | Build tool and dev server |
| **React Router** | 6.21.0 | Client-side routing |
| **TailwindCSS** | 3.4.0 | Utility-first CSS framework |
| **Lucide React** | 0.303.0 | Icon library |
| **PostCSS** | 8.4.32 | CSS processing |
| **Autoprefixer** | 10.4.16 | CSS vendor prefixing |

### 3.3 External Services

| Service | Purpose |
|---------|---------|
| **Perplexity AI** | LLM for content generation (model: sonar) |

---

## 4. Backend Documentation

### 4.1 File Structure

```
backend/
├── main.py              # FastAPI app, routes, CORS config
├── models.py            # Pydantic models for all data structures
├── course_generator.py  # Course creation and regeneration logic
├── quiz_service.py      # Quiz grading, difficulty adaptation
├── llm_service.py       # Perplexity API integration, prompts
├── storage.py           # JSON file persistence operations
├── auth.py              # JWT authentication logic
├── auth_models.py       # User authentication models
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in git)
├── .env.example         # Environment template
└── data/                # Runtime data storage
    ├── courses/         # Course JSON files
    ├── progress/        # User progress JSON files
    ├── feedback/        # Feedback history JSON files
    ├── versions/        # Content version history
    ├── quiz_memory/     # Quiz attempt memory
    └── users.json       # User accounts
```

### 4.2 Core Modules

#### 4.2.1 main.py - API Router

**Purpose**: Entry point for the FastAPI application. Defines all API endpoints and middleware.

**Key Components**:
- CORS middleware configuration (allows localhost:5173, localhost:3000)
- Authentication endpoints (/auth/*)
- Course endpoints (/courses/*, /generate-course, /regenerate-course)
- Quiz endpoints (/quiz/*, /submit-quiz, /generate-quiz)
- Progress endpoints (/progress/*)
- Feedback endpoints (/feedback)
- Health check endpoint (/health)

**Startup Event**:
```python
@app.on_event("startup")
async def startup_event():
    ensure_storage_exists()  # Creates data directories
```

#### 4.2.2 models.py - Data Models

**Purpose**: Defines all Pydantic models for type safety and validation.

**Key Models**:

```python
# Enumerations
class BloomLevel(str, Enum):
    REMEMBER = "Remember"
    UNDERSTAND = "Understand"
    APPLY = "Apply"
    ANALYZE = "Analyze"
    EVALUATE = "Evaluate"
    CREATE = "Create"

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class CourseDifficulty(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"

# Core Content Models
class QuizQuestion          # Quiz question with options, answer, explanation
class LessonContent         # Structured lesson with intro, concepts, examples
class Lesson                # Lesson with content, quiz, Bloom level
class Module                # Module containing lessons
class Course                # Full course with modules

# Request/Response Models
class CourseGenerationRequest   # Topic, duration, difficulty
class CourseGenerationResponse  # Success status, course, message
class QuizSubmission           # User answers to quiz
class QuizResult               # Score, feedback, difficulty update
class FeedbackRequest          # User feedback for content
class FeedbackResponse         # Regeneration result

# Progress Models
class LessonProgress     # Individual lesson progress
class ModuleProgress     # Module-level progress
class CourseProgress     # Overall course progress with all modules
```

#### 4.2.3 course_generator.py - Course Generation

**Purpose**: Orchestrates course creation using LLM service.

**Key Functions**:

```python
async def generate_course(request: CourseGenerationRequest, user_id: str)
    """
    Main entry point for course generation.
    1. Calls LLM service for content
    2. Validates and builds Course object
    3. Saves to storage
    4. Returns success/failure
    """

async def regenerate_course(course_id, topic, duration, difficulty, user_id)
    """Regenerate entire course with same parameters"""

def validate_and_build_course(raw_data, topic, duration, difficulty)
    """
    Converts raw LLM JSON into proper Course model.
    - Parses modules, lessons, quizzes
    - Adds UUIDs where missing
    - Validates Bloom levels and difficulty
    - Builds structured LessonContent
    """

def build_lesson_content(content_data, topic, bloom_level)
    """
    Converts content dict to LessonContent model.
    Handles both structured and legacy string formats.
    """
```

#### 4.2.4 quiz_service.py - Quiz Management

**Purpose**: Handles quiz grading, difficulty adaptation, and quiz generation.

**Key Functions**:

```python
def grade_quiz(questions, answers)
    """
    Grade quiz and return detailed feedback.
    Returns: (score, correct_count, total, feedback_list)
    """

def calculate_new_difficulty(current_difficulty, score)
    """
    Adjust difficulty based on score.
    - >= 85%: Increase difficulty
    - < 50%: Decrease difficulty
    - Otherwise: Stay same
    """

def calculate_new_bloom_level(current_bloom, score, passed)
    """
    Adjust Bloom level based on performance.
    Similar thresholds to difficulty adjustment.
    """

def process_quiz_submission(submission, user_id)
    """
    Main entry point for quiz grading.
    1. Loads course and finds lesson
    2. Grades the submission
    3. Calculates new difficulty/Bloom level
    4. Updates progress in storage
    5. Returns QuizResult
    """

async def generate_quiz_for_lesson(course_id, lesson_id, difficulty, num_questions)
    """
    Generate new quiz questions using LLM.
    Called for quiz regeneration or retake.
    """

async def generate_retake_quiz(course_id, lesson_id, user_id)
    """
    Generate quiz for retake with adjusted difficulty.
    Considers user's progress history.
    """

def calculate_mastery_level(best_score, quiz_attempts)
    """
    Determine human-readable mastery level.
    Returns: {level, description, color, score}
    
    Levels:
    - Not Started (0 attempts)
    - Needs Practice (< 50%)
    - Developing (50-69%)
    - Proficient (70-84%)
    - Mastered (85%+)
    """
```

**Constants**:
```python
PASS_THRESHOLD = 70.0       # Minimum to pass quiz
MASTERY_THRESHOLD = 85.0    # Score for mastery
STRUGGLING_THRESHOLD = 50.0 # Score indicating difficulty
```

#### 4.2.5 llm_service.py - LLM Integration

**Purpose**: Handles all communication with Perplexity AI API.

**Configuration**:
```python
USE_MOCK = os.getenv("USE_MOCK_LLM", "false") == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.perplexity.ai")
MODEL_NAME = os.getenv("LLM_MODEL", "sonar")
TEMPERATURE = 0.7
MAX_TOKENS = 8000
MAX_RETRIES = 3
```

**Key Functions**:

```python
async def generate_course_content(topic, duration_hours, difficulty)
    """
    Generate complete course structure via LLM.
    Uses detailed prompt with Bloom's Taxonomy requirements.
    """

async def generate_quiz_content(lesson_content, bloom_level, difficulty, num_questions)
    """
    Generate quiz questions for lesson content.
    Ensures questions align with specified Bloom level.
    """

async def regenerate_lesson_content(original_content, feedback_type, comments)
    """
    Regenerate lesson based on user feedback.
    Feedback types: too_easy, too_hard, unclear, more_examples
    """

async def call_llm_with_retry(prompt, validator, topic)
    """
    Call LLM with retry logic.
    - MAX_RETRIES attempts
    - JSON validation on each attempt
    - Optional topic relevance check
    """

def validate_json(response)
    """
    Validate LLM response is valid JSON.
    Multiple repair attempts:
    1. Direct parse
    2. Fix common issues
    3. Extract JSON array (for quizzes)
    4. Extract JSON object
    5. Truncate at brackets
    6. Aggressive quiz repair (regex)
    """

def repair_quiz_json(text)
    """
    Aggressively extract quiz data from malformed JSON.
    Uses regex to find question patterns even in broken responses.
    """
```

**Bloom's Taxonomy Prompts**:
```python
BLOOM_LEVELS = {
    "Remember": {
        "description": "Recall facts and basic concepts",
        "teaching_approach": "Focus on definitions, key terms...",
        "verbs": ["define", "list", "name", "identify"],
        "question_types": ["What is...", "List the...", "Name the..."]
    },
    # ... similar for Understand, Apply, Analyze, Evaluate, Create
}
```

#### 4.2.6 storage.py - Data Persistence

**Purpose**: JSON file-based storage operations.

**Storage Structure**:
```
data/
├── courses/{course_id}.json     # Full course data
├── progress/{course_id}_{user_id}.json  # User progress
├── feedback/{course_id}_feedback.json   # Feedback history
├── versions/                    # Content version history
├── quiz_memory/                 # Quiz attempt tracking
└── users.json                   # User accounts
```

**Key Functions**:

```python
# Course Operations
def save_course(course: Course) -> bool
def load_course(course_id: str) -> Optional[Course]
def list_courses(user_id: str) -> List[dict]
def delete_course(course_id: str, user_id: str) -> bool

# Progress Operations
def save_progress(progress: CourseProgress) -> bool
def load_progress(course_id: str, user_id: str) -> Optional[CourseProgress]
def get_or_create_progress(course_id: str, user_id: str) -> CourseProgress
def update_lesson_progress(course_id, module_id, lesson_id, score, ...)

# Feedback Operations
def save_feedback(course_id: str, feedback: dict) -> bool
def get_feedback_history(course_id: str) -> List[dict]

# User Operations (via auth.py)
def load_users() -> list[dict]
def save_users(users: list[dict])
```

#### 4.2.7 auth.py - Authentication

**Purpose**: JWT-based user authentication.

**Configuration**:
```python
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "...")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
```

**Key Functions**:

```python
def create_user(email: str, password: str) -> User
    """Create new user with Argon2 hashed password"""

def authenticate_user(email: str, password: str) -> Optional[dict]
    """Verify email/password, return user if valid"""

def create_access_token(data: dict) -> str
    """Generate JWT token with 24-hour expiry"""

def decode_token(token: str) -> Optional[dict]
    """Validate and decode JWT token"""

async def get_current_user(credentials) -> dict
    """
    FastAPI dependency to extract user from JWT.
    Usage: Depends(get_current_user)
    """
```

---

## 5. Frontend Documentation

### 5.1 File Structure

```
frontend/
├── index.html              # HTML entry point
├── package.json            # Dependencies and scripts
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # TailwindCSS configuration
├── postcss.config.js       # PostCSS plugins
└── src/
    ├── main.jsx            # React entry point
    ├── App.jsx             # Root component with routing
    ├── api.js              # API client functions
    ├── index.css           # Global styles (Tailwind)
    ├── components/         # Reusable UI components
    │   ├── Layout.jsx              # App shell with navigation
    │   ├── ProtectedRoute.jsx      # Auth route guard
    │   ├── CourseGenerator.jsx     # Course creation form
    │   ├── CourseCard.jsx          # Course list item
    │   ├── CourseConfirmationModal.jsx  # Confirm/regenerate modal
    │   ├── LessonContent.jsx       # Lesson display component
    │   ├── FeedbackPanel.jsx       # Lesson feedback form
    │   ├── BloomBadge.jsx          # Bloom level indicator
    │   ├── DifficultyBadge.jsx     # Difficulty indicator
    │   ├── ProgressBar.jsx         # Progress visualization
    │   ├── MasteryIndicator.jsx    # Mastery level display
    │   ├── QuizFeedbackModal.jsx   # Post-quiz feedback
    │   └── WrongAnswerFeedbackModal.jsx  # Wrong answer feedback
    ├── contexts/
    │   └── AuthContext.jsx         # Authentication state
    └── pages/
        ├── HomePage.jsx            # Course list and generator
        ├── LoginPage.jsx           # User login
        ├── RegisterPage.jsx        # User registration
        ├── CoursePage.jsx          # Course overview
        ├── LessonPage.jsx          # Lesson content view
        ├── QuizPage.jsx            # Quiz interface
        └── ProgressPage.jsx        # Progress dashboard
```

### 5.2 Routing Structure

```jsx
// App.jsx - Route Configuration
<Routes>
  {/* Public Routes */}
  <Route path="/login" element={<LoginPage />} />
  <Route path="/register" element={<RegisterPage />} />
  
  {/* Protected Routes (require authentication) */}
  <Route element={<Layout />}>
    <Route path="/" element={
      <ProtectedRoute><HomePage /></ProtectedRoute>
    } />
    <Route path="/course/:courseId" element={
      <ProtectedRoute><CoursePage /></ProtectedRoute>
    } />
    <Route path="/course/:courseId/lesson/:lessonId" element={
      <ProtectedRoute><LessonPage /></ProtectedRoute>
    } />
    <Route path="/course/:courseId/lesson/:lessonId/quiz" element={
      <ProtectedRoute><QuizPage /></ProtectedRoute>
    } />
    <Route path="/course/:courseId/progress" element={
      <ProtectedRoute><ProgressPage /></ProtectedRoute>
    } />
  </Route>
</Routes>
```

### 5.3 State Management

**AuthContext.jsx** - Global authentication state:

```jsx
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load token from localStorage on mount
  useEffect(() => {
    const savedToken = localStorage.getItem(TOKEN_KEY);
    if (savedToken) setToken(savedToken);
    setLoading(false);
  }, []);

  const login = (newToken) => {
    localStorage.setItem(TOKEN_KEY, newToken);
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, login, logout, isAuthenticated: !!token, loading }}>
      {children}
    </AuthContext.Provider>
  );
}
```

### 5.4 API Client (api.js)

**Base Configuration**:
```javascript
const API_BASE = 'http://localhost:8000';
const TOKEN_KEY = 'quiz_app_token';

async function fetchApi(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  // Add JWT token if available
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(url, {
    ...options,
    headers: { ...defaultHeaders, ...options.headers },
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `API error: ${response.status}`);
  }
  
  return response.json();
}
```

**Available API Functions**:

```javascript
// Authentication
register(email, password)
login(email, password)
getCurrentUser()

// Courses
generateCourse(topic, durationHours, difficulty)
regenerateCourse(courseId, topic, durationHours, difficulty)
confirmCourse(courseId)
getCourses()
getCourse(courseId)
deleteCourse(courseId)

// Quizzes
getQuiz(courseId, lessonId)
generateQuiz(courseId, lessonId, difficulty, numQuestions)
submitQuiz(courseId, lessonId, answers)
retakeQuiz(courseId, lessonId)
regenerateEasierQuiz(courseId, lessonId)

// Progress
getProgress(courseId)
getAllProgress()
trackLessonAccess(courseId, moduleIndex, lessonIndex, lessonId)
markLessonCompleted(courseId, lessonId)

// Feedback
submitFeedback(courseId, moduleId, lessonId, feedbackType, comments)
getFeedbackHistory(courseId)

// Utility
healthCheck()
```

### 5.5 Key Components

#### CourseGenerator.jsx
- Form for creating new courses
- Topic input with suggested topics
- Duration slider (1-20 hours)
- Difficulty selector (Beginner/Intermediate/Advanced)
- Loading state during generation

#### LessonContent.jsx
- Renders structured lesson content
- Sections: Introduction, Overview, Core Concepts, Examples, etc.
- Code block rendering with syntax highlighting
- Handles both structured and legacy content formats

#### QuizPage.jsx
- Question navigation with dot indicators
- Answer selection with option highlighting
- Submit button and loading states
- Results display with score and feedback
- Feedback prompt for wrong answers
- "Regenerate easier quiz" functionality
- Full-screen loading overlay during regeneration

#### FeedbackPanel.jsx
- Allows users to request content improvements
- Feedback types: Too Easy, Too Hard, Unclear, More Examples
- Optional additional comments
- Triggers content regeneration via LLM

---

## 6. Database Schema & Storage

### 6.1 JSON File Storage Architecture

The application uses a JSON file-based storage system for simplicity and portability.

### 6.2 Course Schema

**File**: `data/courses/{course_id}.json`

```json
{
  "id": "uuid-string",
  "user_id": "uuid-string",
  "title": "Course Title",
  "topic": "Original Topic",
  "overview": "Course description",
  "duration_hours": 4,
  "difficulty": "Intermediate",
  "confirmed": true,
  "created_at": "2026-01-30T10:00:00",
  "version": 1,
  "modules": [
    {
      "module_id": "uuid-string",
      "module_title": "Module 1: Introduction",
      "module_description": "Module overview",
      "lessons": [
        {
          "lesson_id": "uuid-string",
          "lesson_title": "Lesson Title",
          "bloom_level": "Remember",
          "learning_outcomes": ["Outcome 1", "Outcome 2"],
          "estimated_duration_minutes": 30,
          "content": {
            "introduction": "Intro text...",
            "lesson_overview": ["Point 1", "Point 2"],
            "core_concepts": [
              {
                "title": "Concept Title",
                "explanation": "Detailed explanation",
                "code_example": "code here"
              }
            ],
            "guided_walkthrough": ["Step 1", "Step 2", "Step 3"],
            "practical_examples": [
              {
                "description": "Example description",
                "code": "example code",
                "explanation": "Why this works"
              }
            ],
            "common_pitfalls": ["Pitfall 1"],
            "mental_model": "Think of it like...",
            "summary": "In summary...",
            "further_thinking": ["Question 1"]
          },
          "quiz": [
            {
              "question_id": "uuid-string",
              "question": "Question text?",
              "options": ["A", "B", "C", "D"],
              "correct_answer": "A",
              "difficulty": "medium",
              "bloom_level": "Remember",
              "explanation": "Why A is correct"
            }
          ]
        }
      ]
    }
  ]
}
```

### 6.3 Progress Schema

**File**: `data/progress/{course_id}_{user_id}.json`

```json
{
  "course_id": "uuid-string",
  "user_id": "uuid-string",
  "current_module_index": 0,
  "current_lesson_index": 1,
  "completed_lessons": ["lesson-id-1", "lesson-id-2"],
  "overall_progress": 33.33,
  "started_at": "2026-01-30T10:00:00",
  "last_accessed_at": "2026-01-30T14:30:00",
  "modules": {
    "module-id-1": {
      "module_id": "module-id-1",
      "lessons": {
        "lesson-id-1": {
          "lesson_id": "lesson-id-1",
          "completed": true,
          "quiz_attempts": 2,
          "best_score": 85.0,
          "current_difficulty": "hard",
          "current_bloom_level": "Understand",
          "smoothed_score": 0.72,
          "attempt_history": [
            {
              "attempt_number": 1,
              "score": 66.67,
              "passed": false,
              "feedback": null,
              "timestamp": "2026-01-30T11:00:00"
            },
            {
              "attempt_number": 2,
              "score": 85.0,
              "passed": true,
              "feedback": null,
              "timestamp": "2026-01-30T12:00:00"
            }
          ]
        }
      }
    }
  }
}
```

### 6.4 User Schema

**File**: `data/users.json`

```json
[
  {
    "id": "uuid-string",
    "email": "user@example.com",
    "password_hash": "$argon2id$...",
    "created_at": "2026-01-30T09:00:00"
  }
]
```

---

## 7. API Reference

### 7.1 Authentication Endpoints

#### POST /auth/register
Register a new user.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response** (201):
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

#### POST /auth/login
Authenticate user.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response** (200):
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

#### GET /auth/me
Get current user info. **Requires Authentication**.

**Response** (200):
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "created_at": "2026-01-30T09:00:00"
}
```

### 7.2 Course Endpoints

#### POST /generate-course
Generate a new course. **Requires Authentication**.

**Request**:
```json
{
  "topic": "Machine Learning Fundamentals",
  "duration_hours": 4,
  "difficulty": "Intermediate"
}
```

**Response** (200):
```json
{
  "success": true,
  "course": { /* Full course object */ },
  "message": "Course generated successfully"
}
```

#### GET /courses
List user's courses. **Requires Authentication**.

**Response** (200):
```json
[
  {
    "id": "uuid-string",
    "title": "Course Title",
    "topic": "Topic",
    "duration_hours": 4,
    "difficulty": "Intermediate",
    "confirmed": true,
    "created_at": "2026-01-30T10:00:00",
    "module_count": 3
  }
]
```

#### GET /courses/{course_id}
Get full course details. **Requires Authentication**.

#### DELETE /courses/{course_id}
Delete a course. **Requires Authentication**.

#### PATCH /courses/{course_id}/confirm
Confirm a course for use. **Requires Authentication**.

#### POST /regenerate-course
Regenerate an existing course. **Requires Authentication**.

### 7.3 Quiz Endpoints

#### GET /quiz/{course_id}/{lesson_id}
Get quiz questions. **Requires Authentication**.

**Response** (200):
```json
{
  "lesson_id": "uuid-string",
  "lesson_title": "Lesson Title",
  "current_difficulty": "medium",
  "current_bloom_level": "Understand",
  "questions": [
    {
      "question_id": "uuid-string",
      "question": "Question text?",
      "options": ["A", "B", "C", "D"],
      "difficulty": "medium",
      "bloom_level": "Understand",
      "correct_answer": "A"
    }
  ]
}
```

#### POST /submit-quiz
Submit quiz answers. **Requires Authentication**.

**Request**:
```json
{
  "course_id": "uuid-string",
  "lesson_id": "uuid-string",
  "answers": {
    "question-id-1": "Selected Answer A",
    "question-id-2": "Selected Answer C"
  }
}
```

**Response** (200):
```json
{
  "course_id": "uuid-string",
  "lesson_id": "uuid-string",
  "score": 66.67,
  "correct_count": 2,
  "total_questions": 3,
  "passed": false,
  "needs_feedback": true,
  "updated_difficulty": "medium",
  "current_bloom_level": "Understand",
  "next_bloom_level": "Understand",
  "feedback": [
    {
      "question_id": "uuid-string",
      "question": "Question text?",
      "options": ["A", "B", "C", "D"],
      "user_answer": "A",
      "correct_answer": "A",
      "is_correct": true,
      "explanation": "Explanation text",
      "difficulty": "medium",
      "bloom_level": "Understand"
    }
  ],
  "timestamp": "2026-01-30T12:00:00"
}
```

#### POST /quiz/retake
Retake quiz with adjusted difficulty. **Requires Authentication**.

**Request**:
```json
{
  "course_id": "uuid-string",
  "lesson_id": "uuid-string"
}
```

#### POST /quiz/regenerate-easier
Regenerate quiz at lower difficulty. **Requires Authentication**.

#### POST /generate-quiz
Generate new quiz questions. **Requires Authentication**.

### 7.4 Progress Endpoints

#### GET /progress/{course_id}
Get course progress. **Requires Authentication**.

#### GET /progress/all
Get all course progress. **Requires Authentication**.

#### POST /progress/lesson-access
Track lesson access. **Requires Authentication**.

#### POST /progress/lesson-complete/{course_id}/{lesson_id}
Mark lesson complete. **Requires Authentication**.

### 7.5 Feedback Endpoints

#### POST /feedback
Submit content feedback. **Requires Authentication**.

**Request**:
```json
{
  "course_id": "uuid-string",
  "module_id": "uuid-string",
  "lesson_id": "uuid-string",
  "feedback_type": "too_hard",
  "additional_comments": "Optional comments"
}
```

**Feedback Types**: `too_easy`, `too_hard`, `unclear`, `more_examples`, `different_approach`

#### GET /feedback/{course_id}
Get feedback history. **Requires Authentication**.

### 7.6 Health Check

#### GET /health
Check backend status.

**Response** (200):
```json
{
  "status": "healthy",
  "service": "AI Course Generator",
  "llm_mode": "live",
  "api_key_configured": true,
  "model": "sonar",
  "base_url": "https://api.perplexity.ai"
}
```

---

## 8. Authentication System

### 8.1 Overview

The application uses JWT (JSON Web Token) based authentication with Argon2 password hashing.

### 8.2 Security Features

| Feature | Implementation |
|---------|----------------|
| Password Hashing | Argon2id (modern, memory-hard algorithm) |
| Token Type | JWT (JSON Web Token) |
| Token Expiry | 24 hours |
| Token Storage | localStorage (client-side) |
| Token Transmission | Authorization header (Bearer scheme) |

### 8.3 Authentication Flow

```
Registration:
1. User submits email + password
2. Server hashes password with Argon2
3. Server stores user in users.json
4. Server generates JWT token
5. Client stores token in localStorage

Login:
1. User submits email + password
2. Server verifies password against hash
3. Server generates JWT token
4. Client stores token in localStorage

Protected Requests:
1. Client includes token in Authorization header
2. Server decodes and validates JWT
3. Server extracts user_id from token
4. Request proceeds if valid, 401 if invalid
```

### 8.4 JWT Token Structure

```json
{
  "sub": "user-uuid",    // Subject (user ID)
  "exp": 1706700000      // Expiration timestamp
}
```

---

## 9. LLM Integration

### 9.1 Provider Configuration

The system uses **Perplexity AI** as the LLM provider, accessed via OpenAI-compatible API.

```python
OPENAI_BASE_URL = "https://api.perplexity.ai"
MODEL_NAME = "sonar"
TEMPERATURE = 0.7
MAX_TOKENS = 8000
MAX_RETRIES = 3
```

### 9.2 Prompt Engineering

#### Course Generation Prompt Structure:

```
System Prompt:
- Role: Professional programming course author
- Critical rules: No summarizing, comprehensive content
- JSON output requirements: Proper escaping, no markdown

User Prompt:
- Topic and duration specifications
- Bloom's Taxonomy requirements
- Detailed JSON schema for course structure
- Section requirements (intro, concepts, examples, quiz)
```

#### Quiz Generation Prompt Structure:

```
Generate {num_questions} quiz questions based on this lesson content.

LESSON CONTENT:
{lesson_content}

REQUIREMENTS:
1. Questions must test {bloom_level} level
2. Difficulty: {difficulty}
3. Each question: exactly 4 options, 1 correct answer
4. Include explanation for correct answer

CRITICAL: Output ONLY valid JSON array.
```

### 9.3 Response Validation

The system includes robust JSON validation with multiple repair attempts:

1. **Direct Parse**: Try parsing raw response
2. **Fix Common Issues**: Remove control characters, fix escapes
3. **Extract Array**: Regex for JSON arrays (quiz responses)
4. **Extract Object**: Regex for JSON objects
5. **Truncate/Balance**: Fix unbalanced brackets/braces
6. **Aggressive Repair**: Regex extraction of quiz patterns

### 9.4 Error Handling

- **Rate Limit**: Caught and reported to user
- **Connection Error**: Retry up to MAX_RETRIES
- **JSON Parse Error**: Multiple repair attempts
- **Validation Error**: Detailed error message

---

## 10. Bloom's Taxonomy Implementation

### 10.1 The Six Cognitive Levels

```
┌─────────────────────────────────────────────────────────────┐
│                     BLOOM'S TAXONOMY                        │
│                   (Higher-Order Thinking)                   │
│                                                             │
│   ┌─────────┐                                               │
│   │ CREATE  │ ← Produce new or original work                │
│   ├─────────┤   Verbs: create, design, develop, formulate   │
│   │EVALUATE │ ← Justify decisions and actions               │
│   ├─────────┤   Verbs: evaluate, judge, critique, assess    │
│   │ ANALYZE │ ← Draw connections among ideas                │
│   ├─────────┤   Verbs: analyze, differentiate, examine      │
│   │  APPLY  │ ← Use information in new situations           │
│   ├─────────┤   Verbs: apply, demonstrate, solve, use       │
│   │UNDERSTAND│ ← Explain ideas and concepts                 │
│   ├─────────┤   Verbs: explain, describe, summarize         │
│   │REMEMBER │ ← Recall facts and basic concepts             │
│   └─────────┘   Verbs: define, list, name, identify         │
│                   (Lower-Order Thinking)                    │
└─────────────────────────────────────────────────────────────┘
```

### 10.2 Implementation Details

Each Bloom level has associated:
- **Description**: What the level tests
- **Teaching Approach**: How to teach at this level
- **Content Style**: How to write content
- **Verbs**: Action words for objectives
- **Question Types**: Types of quiz questions

### 10.3 Course Structure Mapping

Courses are structured to progress through Bloom levels:

```
Module 1: Foundations
├── Lesson 1: Introduction (Remember)
├── Lesson 2: Core Concepts (Understand)

Module 2: Application
├── Lesson 3: Practical Usage (Apply)
├── Lesson 4: Problem Solving (Apply)

Module 3: Advanced
├── Lesson 5: Deep Analysis (Analyze)
├── Lesson 6: Best Practices (Evaluate)
├── Lesson 7: Building Projects (Create)
```

### 10.4 Dynamic Level Adjustment

Users progress through Bloom levels based on quiz performance:

- **Score ≥ 85%**: Move UP one level
- **Score < 50%**: Move DOWN one level
- **Otherwise**: Stay at current level

---

## 11. Adaptive Learning Algorithms

### 11.1 Difficulty Adaptation

**Algorithm**: Score-based threshold system

```python
def calculate_new_difficulty(current_difficulty, score):
    difficulty_order = [EASY, MEDIUM, HARD]
    current_index = difficulty_order.index(current_difficulty)
    
    if score >= 85.0:  # Mastery threshold
        if current_index < 2:
            return difficulty_order[current_index + 1]
    elif score < 50.0:  # Struggling threshold
        if current_index > 0:
            return difficulty_order[current_index - 1]
    
    return current_difficulty
```

### 11.2 Exponential Smoothing

Used to prevent difficulty swinging wildly after single attempts:

```
new_score = α × current_result + (1 - α) × previous_score

Where:
  α (alpha) = 0.3
  current_result = quiz score (0-1 scale)
  previous_score = smoothed historical score
```

**Example**:
```
Previous smoothed: 0.50
New quiz score: 0.80

new_score = 0.3 × 0.80 + 0.7 × 0.50
          = 0.24 + 0.35
          = 0.59

Result: Gradual increase, not immediate jump
```

### 11.3 Mastery Level Calculation

```python
def calculate_mastery_level(best_score, quiz_attempts):
    if quiz_attempts == 0:
        return {"level": "Not Started", "color": "gray"}
    
    if best_score >= 85:
        return {"level": "Mastered", "color": "emerald"}
    elif best_score >= 70:
        return {"level": "Proficient", "color": "blue"}
    elif best_score >= 50:
        return {"level": "Developing", "color": "amber"}
    else:
        return {"level": "Needs Practice", "color": "rose"}
```

---

## 12. Quiz System

### 12.1 Quiz Flow

```
┌─────────────────┐
│ Load Quiz       │
│ (GET /quiz)     │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Display         │
│ Questions       │
│ (one at a time) │
└────────┬────────┘
         ▼
┌─────────────────┐
│ User Answers    │
│ (optional per Q)│
└────────┬────────┘
         ▼
┌─────────────────┐
│ Submit Quiz     │
│ (POST /submit)  │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Show Results    │
│ + Feedback      │
└────────┬────────┘
         ▼
    ┌────┴────┐
    │ Wrong   │
    │ Answers?│
    └────┬────┘
      Yes│
         ▼
┌─────────────────┐
│ Feedback Prompt │
│ - Regenerate    │
│ - Show Explain  │
│ - Skip          │
└─────────────────┘
```

### 12.2 Quiz Question Structure

```json
{
  "question_id": "unique-uuid",
  "question": "Clear question text?",
  "options": [
    "Option A (correct)",
    "Option B",
    "Option C", 
    "Option D"
  ],
  "correct_answer": "Option A (correct)",
  "difficulty": "medium",
  "bloom_level": "Understand",
  "explanation": "Detailed explanation of why A is correct"
}
```

### 12.3 Grading Logic

```python
def grade_quiz(questions, answers):
    correct_count = 0
    feedback = []
    
    for question in questions:
        user_answer = answers.get(question.question_id, "")
        is_correct = user_answer == question.correct_answer
        
        if is_correct:
            correct_count += 1
        
        feedback.append({
            "question_id": question.question_id,
            "user_answer": user_answer,
            "correct_answer": question.correct_answer,
            "is_correct": is_correct,
            "explanation": question.explanation
        })
    
    score = (correct_count / len(questions)) * 100
    return score, correct_count, len(questions), feedback
```

### 12.4 Post-Quiz Feedback Options

When user has wrong answers:

1. **"Quiz is too hard - Give me easier questions"**
   - Lowers difficulty by one level
   - Regenerates quiz questions via LLM
   
2. **"I need more explanation"**
   - Shows expanded explanations for wrong answers
   - Does not regenerate quiz

3. **"Skip"**
   - Closes feedback prompt
   - Shows standard results

---

## 13. Progress Tracking

### 13.1 Tracked Metrics

| Metric | Description |
|--------|-------------|
| `overall_progress` | Percentage of lessons completed |
| `current_module_index` | Last accessed module |
| `current_lesson_index` | Last accessed lesson |
| `completed_lessons` | List of completed lesson IDs |
| `quiz_attempts` | Number of attempts per lesson |
| `best_score` | Highest score achieved |
| `current_difficulty` | Current quiz difficulty level |
| `current_bloom_level` | Current Bloom's Taxonomy level |
| `smoothed_score` | Exponentially smoothed score |

### 13.2 Progress Calculation

```python
overall_progress = (len(completed_lessons) / total_lessons) * 100
```

### 13.3 Resume Functionality

The system tracks `current_module_index` and `current_lesson_index` to enable:

- "Continue Learning" section on home page
- Jump directly to last accessed lesson
- Show progress indicators across courses

---

## 14. Configuration & Environment

### 14.1 Backend Environment (.env)

```env
# LLM Configuration
USE_MOCK_LLM=false                    # Set to "true" for mock mode
OPENAI_API_KEY=your-perplexity-key    # Perplexity API key
OPENAI_BASE_URL=https://api.perplexity.ai
LLM_MODEL=sonar                        # Perplexity model name

# Authentication
JWT_SECRET_KEY=your-secure-secret-key-change-in-production
```

### 14.2 Frontend Configuration

**vite.config.js**:
```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173
  }
})
```

**tailwind.config.js**:
```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: { extend: {} },
  plugins: [],
}
```

---

## 15. Deployment Guide

### 15.1 Development Setup

**Backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

### 15.2 Production Considerations

1. **Backend**:
   - Use production ASGI server (e.g., Gunicorn with Uvicorn workers)
   - Set strong JWT_SECRET_KEY
   - Consider database migration from JSON files
   - Enable HTTPS

2. **Frontend**:
   - Build for production: `npm run build`
   - Serve with nginx or CDN
   - Update API_BASE for production URL

3. **Security**:
   - Change default JWT secret
   - Use HTTPS everywhere
   - Consider rate limiting
   - Implement proper CORS for production domains

---

## 16. Troubleshooting

### 16.1 Common Issues

#### Backend won't start
```bash
# Check if port is in use
lsof -i :8000
# Kill existing process
kill -9 <PID>
```

#### LLM generating invalid JSON
- Check backend logs for raw response
- Verify API key is valid
- System includes multiple JSON repair attempts

#### CORS errors in browser
- Verify backend CORS middleware includes frontend URL
- Check that frontend is using correct API_BASE

#### Authentication failing
- Clear localStorage and re-login
- Check token expiration (24 hours)
- Verify JWT_SECRET_KEY hasn't changed

### 16.2 Logging

Backend logs are written to stdout. Key log patterns:

```
[COURSE GENERATION] - Course generation events
[QUIZ GENERATION] - Quiz generation events
[LLM] - LLM API calls and responses
[JSON REPAIR] - JSON validation attempts
```

### 16.3 Debug Mode

Enable verbose logging by checking backend output:
```bash
uvicorn main:app --reload --port 8000
# Logs appear in terminal
```

---

## Appendix A: API Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid/missing token |
| 403 | Forbidden - Not course owner |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Error - Server/LLM failure |

## Appendix B: Bloom Level Question Examples

| Level | Question Type | Example |
|-------|--------------|---------|
| Remember | Recall | "What is the definition of a variable?" |
| Understand | Explain | "Explain why functions are useful" |
| Apply | Solve | "Write a function that calculates..." |
| Analyze | Compare | "Compare the pros and cons of..." |
| Evaluate | Judge | "Which approach is best for..." |
| Create | Design | "Design a system that..." |

---

**End of Documentation**

*This documentation covers version 2.0.0 of the AI-Powered Dynamic Course & Quiz Generator. For updates and contributions, refer to the project repository.*
