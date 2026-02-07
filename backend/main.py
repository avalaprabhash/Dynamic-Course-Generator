"""
AI-Powered Dynamic Course & Quiz Generator - FastAPI Backend

This is the main entry point for the backend API. It provides endpoints for:
- Course generation from topic and duration (LLM-powered)
- Quiz generation for lessons (LLM-powered)
- Quiz submission and grading with adaptive difficulty
- User feedback and content regeneration
- Progress tracking

Architecture Overview:
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React Frontend │────▶│   FastAPI API   │────▶│   LLM Service   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               │                         ▼
                               │                 ┌─────────────────┐
                               │                 │   OpenAI API    │
                               │                 │  (gpt-4o-mini)  │
                               │                 └─────────────────┘
                               ▼
                        ┌─────────────────┐
                        │  JSON Storage   │
                        │  (courses,      │
                        │   progress,     │
                        │   feedback)     │
                        └─────────────────┘

Run with: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel

from models import (
    CourseGenerationRequest, CourseGenerationResponse,
    RegenerateCourseRequest,
    QuizSubmission, QuizResult,
    FeedbackRequest, FeedbackResponse,
    Course, CourseProgress, ProgressUpdate,
    LessonAccessRequest, BloomLevel, QuizRetakeRequest
)
from course_generator import generate_course, regenerate_content, regenerate_course
from quiz_service import (
    process_quiz_submission,
    calculate_mastery_level,
    generate_quiz_for_lesson,
    generate_retake_quiz,
    QuizGenerationRequest,
    GeneratedQuiz
)
from storage import (
    load_course, list_courses, delete_course, save_course,
    get_or_create_progress, load_progress,
    get_feedback_history, ensure_storage_exists, delete_progress,
    update_lesson_access, mark_lesson_completed,
    get_latest_quiz_attempt_memory
)
from auth_models import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from auth import create_user, authenticate_user, create_access_token, get_current_user

# Initialize FastAPI app
app = FastAPI(
    title="AI Course & Quiz Generator",
    description="Generate personalized courses with Bloom's Taxonomy alignment and adaptive quizzes using LLM",
    version="2.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure storage directories exist on startup
@app.on_event("startup")
async def startup_event():
    ensure_storage_exists()


# ============== Authentication Endpoints ==============

@app.post("/auth/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """
    Register a new user account.
    
    - **email**: Valid email address (must be unique)
    - **password**: Password (minimum 6 characters)
    
    Returns a JWT access token for immediate login.
    """
    user = create_user(request.email, request.password)
    access_token = create_access_token(data={"sub": user.id})
    return TokenResponse(access_token=access_token)


@app.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login with email and password.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns a JWT access token valid for 24 hours.
    """
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    access_token = create_access_token(data={"sub": user["id"]})
    return TokenResponse(access_token=access_token)


@app.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current user information.
    
    Requires valid JWT token in Authorization header.
    """
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        created_at=current_user["created_at"]
    )


# ============== Course Endpoints ==============

@app.post("/generate-course", response_model=CourseGenerationResponse)
async def create_course(request: CourseGenerationRequest, current_user: dict = Depends(get_current_user)):
    """
    Generate a new course based on topic and duration using LLM.
    
    Requires authentication. Course is associated with the authenticated user.
    
    The course is structured using Bloom's Taxonomy, progressing from
    basic recall (Remember) to higher-order thinking (Create).
    
    - **topic**: The subject matter for the course (3-200 characters)
    - **duration_hours**: Target course length in hours (1-100)
    
    Returns the complete course structure with modules, lessons, and quizzes.
    """
    user_id = current_user["id"]
    success, course, message = await generate_course(request, user_id)
    
    return CourseGenerationResponse(
        success=success,
        course=course,
        message=message
    )


@app.post("/regenerate-course", response_model=CourseGenerationResponse)
async def regenerate_course_endpoint(request: RegenerateCourseRequest, current_user: dict = Depends(get_current_user)):
    """Regenerate an existing course with the same parameters."""
    user_id = current_user["id"]
    success, course, message = await regenerate_course(
        request.course_id,
        request.topic,
        request.duration_hours,
        request.difficulty.value,
        user_id
    )
    return CourseGenerationResponse(success=success, course=course, message=message)


@app.patch("/courses/{course_id}/confirm")
async def confirm_course(course_id: str, current_user: dict = Depends(get_current_user)):
    """Mark a course as confirmed by the user."""
    user_id = current_user["id"]
    course = load_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.user_id != user_id:
        raise HTTPException(status_code=403, detail="You don't have permission to confirm this course")
    course.confirmed = True
    save_course(course)
    return {"success": True, "message": "Course confirmed"}


@app.get("/courses", response_model=List[dict])
async def get_courses(current_user: dict = Depends(get_current_user)):
    """
    List courses belonging to the authenticated user.
    
    Returns course ID, title, topic, duration, and creation date.
    Sorted by creation date (newest first).
    Only returns courses created by the current user.
    """
    user_id = current_user["id"]
    return list_courses(user_id)


@app.get("/courses/{course_id}", response_model=Course)
async def get_course(course_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get the full details of a specific course.
    
    Requires authentication and course ownership.
    
    - **course_id**: The unique identifier of the course
    
    Returns the complete course structure including all modules,
    lessons, learning outcomes, and quiz questions.
    """
    user_id = current_user["id"]
    course = load_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.user_id != user_id:
        raise HTTPException(status_code=403, detail="You don't have permission to access this course")
    return course


@app.delete("/courses/{course_id}")
async def remove_course(course_id: str, current_user: dict = Depends(get_current_user)):
    """
    Delete a course from storage.
    
    Requires authentication and course ownership.
    This also removes associated progress and feedback data.
    """
    user_id = current_user["id"]
    if delete_course(course_id, user_id):
        return {"success": True, "message": "Course deleted"}
    raise HTTPException(status_code=404, detail="Course not found or you don't have permission to delete it")


# ============== Quiz Endpoints ==============

@app.post("/generate-quiz")
async def create_quiz(request: QuizGenerationRequest):
    """
    Generate a new quiz for a lesson using LLM.
    
    This endpoint allows dynamic quiz generation based on:
    - The lesson content
    - Bloom's Taxonomy level
    - Desired difficulty
    
    - **course_id**: The course containing the lesson
    - **lesson_id**: The lesson to generate quiz for
    - **difficulty**: easy, medium, or hard
    - **num_questions**: Number of questions (default 3)
    
    Returns generated quiz questions with options and correct answers.
    """
    success, quiz_data, message = await generate_quiz_for_lesson(
        course_id=request.course_id,
        lesson_id=request.lesson_id,
        difficulty=request.difficulty,
        num_questions=request.num_questions
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {
        "success": True,
        "message": message,
        "quiz": quiz_data
    }


@app.post("/submit-quiz", response_model=QuizResult)
async def submit_quiz(submission: QuizSubmission, current_user: dict = Depends(get_current_user)):
    """
    Submit quiz answers and receive graded results.
    
    Requires authentication and course ownership.
    
    The system uses adaptive difficulty:
    - Score >= 85%: Difficulty increases
    - Score < 50%: Difficulty decreases
    - Uses Bloom's Taxonomy for cognitive level progression
    
    - **course_id**: The course containing the quiz
    - **lesson_id**: The specific lesson's quiz
    - **answers**: Dict mapping question_id to selected answer
    
    Returns score, per-question feedback with explanations.
    """
    user_id = current_user["id"]
    
    # Verify course ownership
    course = load_course(submission.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.user_id != user_id:
        raise HTTPException(status_code=403, detail="You don't have permission to submit quiz for this course")
    
    result = process_quiz_submission(submission, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    return result


@app.post("/quiz/retake")
async def retake_quiz(
    request: QuizRetakeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Retake a quiz with difficulty adjusted based on previous performance.
    
    If the user struggled before, the quiz will be easier.
    If the user did well, difficulty is maintained or increased.
    """
    user_id = current_user["id"]
    
    # Verify course ownership
    course = load_course(request.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.user_id != user_id:
        raise HTTPException(status_code=403, detail="You don't have permission to access this course")
    
    # Find the lesson
    target_lesson = None
    for module in course.modules:
        for lesson in module.lessons:
            if lesson.lesson_id == request.lesson_id:
                target_lesson = lesson
                break
        if target_lesson:
            break
    
    if not target_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Generate adapted quiz based on user's progress
    success, quiz_data, message = await generate_retake_quiz(
        course_id=request.course_id,
        lesson_id=request.lesson_id,
        user_id=user_id
    )
    
    if not success:
        raise HTTPException(status_code=500, detail=message)
    
    return {
        "lesson_id": request.lesson_id,
        "lesson_title": quiz_data["lesson_title"],
        "current_difficulty": quiz_data["difficulty"],
        "current_bloom_level": quiz_data["bloom_level"],
        "questions": quiz_data["questions"]
    }


@app.get("/quiz/{course_id}/{lesson_id}")
async def get_quiz(course_id: str, lesson_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get quiz questions for a specific lesson.
    
    Requires authentication and course ownership.
    Returns questions with current difficulty level.
    """
    user_id = current_user["id"]
    course = load_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Verify course ownership
    if course.user_id != user_id:
        raise HTTPException(status_code=403, detail="You don't have permission to access this course's quiz")
    
    for module in course.modules:
        for lesson in module.lessons:
            if lesson.lesson_id == lesson_id:
                progress = load_progress(course_id, user_id)
                current_difficulty = "medium"
                current_bloom = lesson.bloom_level.value
                
                if progress and module.module_id in progress.modules:
                    mod_progress = progress.modules[module.module_id]
                    if lesson_id in mod_progress.get("lessons", {}):
                        lesson_progress = mod_progress["lessons"][lesson_id]
                        current_difficulty = lesson_progress.get("current_difficulty", "medium")
                        current_bloom = lesson_progress.get("current_bloom_level", lesson.bloom_level.value)
                
                questions = []
                for q in lesson.quiz:
                    questions.append({
                        "question_id": q.question_id,
                        "question": q.question,
                        "options": q.options,
                        "difficulty": q.difficulty.value,
                        "bloom_level": q.bloom_level.value,
                        "correct_answer": q.correct_answer
                    })
                
                return {
                    "lesson_id": lesson_id,
                    "lesson_title": lesson.lesson_title,
                    "current_difficulty": current_difficulty,
                    "current_bloom_level": current_bloom,
                    "questions": questions
                }
    
    raise HTTPException(status_code=404, detail="Lesson not found")


@app.post("/quiz/regenerate-easier")
async def regenerate_easier_quiz(
    request: QuizRetakeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Regenerate a quiz with lower difficulty when user finds it too hard.
    
    Lowers the difficulty by one level (hard->medium, medium->easy).
    """
    user_id = current_user["id"]
    
    # Verify course ownership
    course = load_course(request.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.user_id != user_id:
        raise HTTPException(status_code=403, detail="You don't have permission to access this course")
    
    # Find the lesson
    target_lesson = None
    target_module_id = None
    for module in course.modules:
        for lesson in module.lessons:
            if lesson.lesson_id == request.lesson_id:
                target_lesson = lesson
                target_module_id = module.module_id
                break
        if target_lesson:
            break
    
    if not target_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Get current difficulty and lower it
    progress = load_progress(request.course_id, user_id)
    current_difficulty = "medium"
    current_bloom = target_lesson.bloom_level.value
    
    if progress and target_module_id in progress.modules:
        mod_progress = progress.modules[target_module_id]
        if request.lesson_id in mod_progress.get("lessons", {}):
            lesson_progress = mod_progress["lessons"][request.lesson_id]
            current_difficulty = lesson_progress.get("current_difficulty", "medium")
            current_bloom = lesson_progress.get("current_bloom_level", target_lesson.bloom_level.value)
    
    # Lower difficulty
    difficulty_map = {"hard": "medium", "medium": "easy", "easy": "easy"}
    new_difficulty = difficulty_map.get(current_difficulty, "easy")
    
    # Generate easier quiz
    success, quiz_data, message = await generate_quiz_for_lesson(
        course_id=request.course_id,
        lesson_id=request.lesson_id,
        difficulty=new_difficulty,
        num_questions=3,
        bloom_level=current_bloom
    )
    
    if not success:
        raise HTTPException(status_code=500, detail=message)
    
    return {
        "lesson_id": request.lesson_id,
        "lesson_title": quiz_data["lesson_title"],
        "current_difficulty": new_difficulty,
        "current_bloom_level": quiz_data["bloom_level"],
        "questions": quiz_data["questions"],
        "message": "Quiz regenerated with easier questions"
    }


# ============== Feedback & Regeneration Endpoints ==============

@app.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackRequest, current_user: dict = Depends(get_current_user)):
    """
    Submit feedback and trigger content regeneration using LLM.
    
    Requires authentication and course ownership.
    
    Feedback types:
    - **too_easy**: Content is not challenging enough
    - **too_hard**: Content is too difficult
    - **unclear**: Explanations need improvement
    - **more_examples**: Need additional examples
    - **different_approach**: Try a different teaching method
    
    The system regenerates the specified content based on feedback,
    keeping version history for potential rollback.
    """
    user_id = current_user["id"]
    
    # Verify course ownership
    course = load_course(feedback.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.user_id != user_id:
        raise HTTPException(status_code=403, detail="You don't have permission to submit feedback for this course")
    
    success, regenerated, message = await regenerate_content(
        course_id=feedback.course_id,
        module_id=feedback.module_id,
        lesson_id=feedback.lesson_id,
        feedback_type=feedback.feedback_type.value,
        additional_comments=feedback.additional_comments
    )
    
    return FeedbackResponse(
        success=success,
        message=message,
        regenerated_content=regenerated
    )


@app.get("/feedback/{course_id}")
async def get_feedback(course_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get feedback history for a course.
    
    Requires authentication and course ownership.
    Returns all feedback entries with timestamps,
    useful for understanding content evolution.
    """
    user_id = current_user["id"]
    
    # Verify course ownership
    course = load_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.user_id != user_id:
        raise HTTPException(status_code=403, detail="You don't have permission to access this course's feedback")
    
    return get_feedback_history(course_id)


# ============== Progress Endpoints ==============

@app.get("/progress/{course_id}")
async def get_progress(course_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get learning progress for a course.
    
    Requires authentication and course ownership.
    
    Returns:
    - Overall completion percentage
    - Current module and lesson indices
    - Completed lessons list
    - Per-module and per-lesson progress
    - Quiz attempts and best scores
    - Current difficulty levels
    - Mastery status for each lesson
    """
    course = load_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    user_id = current_user["id"]
    
    # Verify course ownership
    if course.user_id != user_id:
        raise HTTPException(status_code=403, detail="You don't have permission to access this course's progress")
    
    progress = get_or_create_progress(course_id, user_id)
    
    detailed_progress = {
        "course_id": course_id,
        "overall_progress": progress.overall_progress,
        "current_module_index": progress.current_module_index,
        "current_lesson_index": progress.current_lesson_index,
        "completed_lessons": progress.completed_lessons,
        "started_at": progress.started_at.isoformat() if progress.started_at else None,
        "last_accessed_at": progress.last_accessed_at.isoformat() if progress.last_accessed_at else None,
        "modules": []
    }
    
    for module in course.modules:
        module_data = {
            "module_id": module.module_id,
            "module_title": module.module_title,
            "lessons": []
        }
        
        for lesson in module.lessons:
            lesson_progress = {"lesson_id": lesson.lesson_id}
            
            if module.module_id in progress.modules:
                mod_prog = progress.modules[module.module_id]
                if lesson.lesson_id in mod_prog.get("lessons", {}):
                    les_prog = mod_prog["lessons"][lesson.lesson_id]
                    lesson_progress.update({
                        "completed": les_prog.get("completed", False),
                        "quiz_attempts": les_prog.get("quiz_attempts", 0),
                        "best_score": les_prog.get("best_score", 0),
                        "current_difficulty": les_prog.get("current_difficulty", "medium"),
                        "mastery": calculate_mastery_level(
                            les_prog.get("smoothed_score", 0),
                            les_prog.get("quiz_attempts", 0)
                        )
                    })
                else:
                    lesson_progress.update({
                        "completed": False,
                        "quiz_attempts": 0,
                        "best_score": 0,
                        "current_difficulty": "medium",
                        "mastery": calculate_mastery_level(0, 0)
                    })
            else:
                lesson_progress.update({
                    "completed": False,
                    "quiz_attempts": 0,
                    "best_score": 0,
                    "current_difficulty": "medium",
                    "mastery": calculate_mastery_level(0, 0)
                })
            
            module_data["lessons"].append(lesson_progress)
        
        detailed_progress["modules"].append(module_data)
    
    return detailed_progress


@app.post("/progress/lesson-access")
async def track_lesson_access(request: LessonAccessRequest, current_user: dict = Depends(get_current_user)):
    """
    Track when a user accesses a lesson.
    
    Updates current_module_index and current_lesson_index for resume functionality.
    """
    user_id = current_user["id"]
    progress = update_lesson_access(
        request.course_id,
        request.module_index,
        request.lesson_index,
        request.lesson_id,
        user_id
    )
    return {
        "success": True,
        "current_module_index": progress.current_module_index,
        "current_lesson_index": progress.current_lesson_index,
        "message": "Lesson access tracked"
    }


@app.post("/progress/lesson-complete/{course_id}/{lesson_id}")
async def complete_lesson(course_id: str, lesson_id: str, current_user: dict = Depends(get_current_user)):
    """
    Mark a lesson as completed.
    
    Adds lesson to completed_lessons list and recalculates overall progress.
    """
    user_id = current_user["id"]
    progress = mark_lesson_completed(course_id, lesson_id, user_id)
    return {
        "success": True,
        "overall_progress": progress.overall_progress,
        "completed_lessons": progress.completed_lessons,
        "message": "Lesson marked as completed"
    }


@app.get("/progress/all")
async def get_all_progress(current_user: dict = Depends(get_current_user)):
    """
    Get progress for all courses for the current user.
    
    Returns a list of courses with progress information for resume functionality.
    Only returns courses owned by the current user.
    """
    user_id = current_user["id"]
    courses = list_courses(user_id)  # Only get user's courses
    progress_list = []
    
    for course in courses:
        progress = load_progress(course["id"], user_id)
        if progress:
            progress_list.append({
                "course_id": course["id"],
                "course_title": course["title"],
                "overall_progress": progress.overall_progress,
                "current_module_index": progress.current_module_index,
                "current_lesson_index": progress.current_lesson_index,
                "completed_lessons": progress.completed_lessons,
                "last_accessed_at": progress.last_accessed_at.isoformat() if progress.last_accessed_at else None
            })
    
    return progress_list


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    from llm_service import USE_MOCK, OPENAI_API_KEY, MODEL_NAME, OPENAI_BASE_URL
    
    return {
        "status": "healthy", 
        "service": "AI Course Generator",
        "llm_mode": "mock" if USE_MOCK else "live",
        "api_key_configured": bool(OPENAI_API_KEY),
        "model": MODEL_NAME,
        "base_url": OPENAI_BASE_URL
    }


# Run directly for development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
