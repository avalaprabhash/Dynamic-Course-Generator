"""
JSON-Based Storage System

This module handles all data persistence using JSON files.
It provides a simple but effective way to store courses, progress, and feedback
without requiring a database setup.

Why JSON Storage?
- Simple to set up and inspect
- Human-readable data files
- Easy to backup and version control
- Sufficient for local/demo usage
"""

import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from models import Course, CourseProgress, LessonProgress, ModuleProgress, Difficulty, BloomLevel, QuizAttemptFeedback, QuizAttemptMemory

# Storage directory - created in the project root
STORAGE_DIR = Path(__file__).parent / "data"


def ensure_storage_exists():
    """Create storage directories if they don't exist"""
    directories = [
        STORAGE_DIR,
        STORAGE_DIR / "courses",
        STORAGE_DIR / "progress",
        STORAGE_DIR / "feedback",
        STORAGE_DIR / "versions",
        STORAGE_DIR / "quiz_memory"
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def _serialize_datetime(obj: Any) -> Any:
    """Convert datetime objects to ISO format strings for JSON serialization"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _parse_datetime(data: dict) -> dict:
    """Parse datetime strings back to datetime objects"""
    datetime_fields = ['created_at', 'started_at', 'last_accessed', 'timestamp']
    for field in datetime_fields:
        if field in data and isinstance(data[field], str):
            try:
                data[field] = datetime.fromisoformat(data[field])
            except (ValueError, TypeError):
                pass
    return data


# ============== Course Storage ==============

def save_course(course: Course) -> bool:
    """
    Save a course to JSON storage.
    
    Args:
        course: The Course object to save
        
    Returns:
        True if successful, False otherwise
    """
    ensure_storage_exists()
    try:
        file_path = STORAGE_DIR / "courses" / f"{course.id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(course.model_dump(), f, indent=2, default=_serialize_datetime)
        return True
    except Exception as e:
        print(f"Error saving course: {e}")
        return False


def load_course(course_id: str) -> Optional[Course]:
    """
    Load a course from storage by its ID.
    
    Args:
        course_id: The unique identifier of the course
        
    Returns:
        Course object if found, None otherwise
    """
    ensure_storage_exists()
    try:
        file_path = STORAGE_DIR / "courses" / f"{course_id}.json"
        if not file_path.exists():
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data = _parse_datetime(data)
            return Course(**data)
    except Exception as e:
        print(f"Error loading course: {e}")
        return None


def list_courses(user_id: str = None) -> List[Dict[str, Any]]:
    """
    List courses with basic metadata.
    
    Args:
        user_id: If provided, only return courses belonging to this user.
                 If None, return all courses (for backwards compatibility).
    
    Returns:
        List of course summaries (id, title, topic, created_at)
    """
    ensure_storage_exists()
    courses = []
    courses_dir = STORAGE_DIR / "courses"
    
    for file_path in courses_dir.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Filter by user_id if provided
                course_user_id = data.get("user_id", "default_user")
                if user_id is not None and course_user_id != user_id:
                    continue
                
                courses.append({
                    "id": data.get("id"),
                    "user_id": course_user_id,
                    "title": data.get("title"),
                    "topic": data.get("topic"),
                    "duration_hours": data.get("duration_hours"),
                    "difficulty": data.get("difficulty"),
                    "confirmed": data.get("confirmed", False),
                    "created_at": data.get("created_at"),
                    "module_count": len(data.get("modules", []))
                })
        except Exception as e:
            print(f"Error reading course file {file_path}: {e}")
    
    # Sort by creation date, newest first
    courses.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return courses


def verify_course_ownership(course_id: str, user_id: str) -> bool:
    """
    Verify that a course belongs to a specific user.
    
    Args:
        course_id: The course to check
        user_id: The user who should own the course
        
    Returns:
        True if the course exists and belongs to the user, False otherwise
    """
    course = load_course(course_id)
    if not course:
        return False
    return course.user_id == user_id


def delete_course(course_id: str, user_id: str = None) -> bool:
    """
    Delete a course from storage.
    
    Args:
        course_id: The course to delete
        user_id: If provided, verify ownership before deleting
    """
    ensure_storage_exists()
    
    # Verify ownership if user_id provided
    if user_id is not None:
        if not verify_course_ownership(course_id, user_id):
            return False
    
    try:
        file_path = STORAGE_DIR / "courses" / f"{course_id}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    except Exception as e:
        print(f"Error deleting course: {e}")
        return False


def delete_progress(course_id: str, user_id: str = "default_user") -> bool:
    """Delete progress for a course and user."""
    ensure_storage_exists()
    try:
        file_path = STORAGE_DIR / "progress" / f"{course_id}_{user_id}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    except Exception as e:
        print(f"Error deleting progress: {e}")
        return False


# ============== Progress Storage ==============

def save_progress(progress: CourseProgress) -> bool:
    """Save course progress to storage"""
    ensure_storage_exists()
    try:
        file_path = STORAGE_DIR / "progress" / f"{progress.course_id}_{progress.user_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(progress.model_dump(), f, indent=2, default=_serialize_datetime)
        return True
    except Exception as e:
        print(f"Error saving progress: {e}")
        return False


def load_progress(course_id: str, user_id: str = "default_user") -> Optional[CourseProgress]:
    """Load progress for a specific course and user"""
    ensure_storage_exists()
    try:
        file_path = STORAGE_DIR / "progress" / f"{course_id}_{user_id}.json"
        if not file_path.exists():
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data = _parse_datetime(data)
            return CourseProgress(**data)
    except Exception as e:
        print(f"Error loading progress: {e}")
        return None


def get_or_create_progress(course_id: str, user_id: str = "default_user") -> CourseProgress:
    """Get existing progress or create new tracking for a course"""
    existing = load_progress(course_id, user_id)
    if existing:
        existing.last_accessed_at = datetime.now()
        save_progress(existing)
        return existing
    
    new_progress = CourseProgress(course_id=course_id, user_id=user_id)
    save_progress(new_progress)
    return new_progress


def update_lesson_progress(
    course_id: str,
    module_id: str,
    lesson_id: str,
    score: float,
    new_difficulty: Difficulty,
    smoothed_score: float,
    bloom_level: BloomLevel = None,
    user_id: str = "default_user"
) -> CourseProgress:
    """
    Update progress after a quiz attempt.
    
    This function updates the lesson's progress including:
    - Quiz attempt count
    - Best score
    - Current difficulty level
    - Current Bloom level
    - Smoothed score for adaptive difficulty
    """
    progress = get_or_create_progress(course_id, user_id)
    
    # Ensure module exists in progress
    if module_id not in progress.modules:
        progress.modules[module_id] = {"module_id": module_id, "lessons": {}}
    
    # Get or create lesson progress
    module_progress = progress.modules[module_id]
    if lesson_id not in module_progress.get("lessons", {}):
        module_progress["lessons"] = module_progress.get("lessons", {})
        module_progress["lessons"][lesson_id] = {
            "lesson_id": lesson_id,
            "completed": False,
            "quiz_attempts": 0,
            "best_score": 0.0,
            "current_difficulty": Difficulty.MEDIUM.value,
            "current_bloom_level": BloomLevel.REMEMBER.value,
            "smoothed_score": 0.5,
            "attempt_history": []
        }
    
    lesson_progress = module_progress["lessons"][lesson_id]
    lesson_progress["quiz_attempts"] += 1
    lesson_progress["best_score"] = max(lesson_progress["best_score"], score)
    lesson_progress["current_difficulty"] = new_difficulty.value
    lesson_progress["smoothed_score"] = smoothed_score
    
    # Update Bloom level if provided
    if bloom_level:
        lesson_progress["current_bloom_level"] = bloom_level.value
    
    # Record this attempt
    if "attempt_history" not in lesson_progress:
        lesson_progress["attempt_history"] = []
    lesson_progress["attempt_history"].append({
        "attempt_number": lesson_progress["quiz_attempts"],
        "score": score,
        "passed": score >= 70,
        "feedback": None,  # Will be updated if feedback is submitted
        "timestamp": datetime.now().isoformat()
    })
    
    # Mark as completed if score is good enough
    if score >= 70:
        lesson_progress["completed"] = True
    
    # Recalculate overall progress
    course = load_course(course_id)
    if course:
        total_lessons = sum(len(m.lessons) for m in course.modules)
        completed_lessons = 0
        for mod_id, mod_data in progress.modules.items():
            for les_id, les_data in mod_data.get("lessons", {}).items():
                if les_data.get("completed", False):
                    completed_lessons += 1
        
        progress.overall_progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    
    progress.last_accessed_at = datetime.now()
    save_progress(progress)
    return progress


def record_quiz_attempt_feedback(
    course_id: str,
    module_id: str,
    lesson_id: str,
    feedback: QuizAttemptFeedback,
    new_bloom_level: BloomLevel,
    user_id: str = "default_user"
) -> CourseProgress:
    """
    Record feedback for the most recent quiz attempt and update Bloom level.
    Called after a failed quiz when user submits feedback.
    """
    progress = get_or_create_progress(course_id, user_id)
    
    if module_id not in progress.modules:
        return progress
    
    module_progress = progress.modules[module_id]
    if lesson_id not in module_progress.get("lessons", {}):
        return progress
    
    lesson_progress = module_progress["lessons"][lesson_id]
    
    # Update the most recent attempt with feedback
    if "attempt_history" in lesson_progress and len(lesson_progress["attempt_history"]) > 0:
        lesson_progress["attempt_history"][-1]["feedback"] = feedback.value
    
    # Update Bloom level based on feedback
    lesson_progress["current_bloom_level"] = new_bloom_level.value
    
    progress.last_accessed_at = datetime.now()
    save_progress(progress)
    return progress


def update_lesson_access(
    course_id: str,
    module_index: int,
    lesson_index: int,
    lesson_id: str,
    user_id: str = "default_user"
) -> CourseProgress:
    """Update progress when a lesson is accessed."""
    progress = get_or_create_progress(course_id, user_id)
    progress.current_module_index = module_index
    progress.current_lesson_index = lesson_index
    progress.last_accessed_at = datetime.now()
    save_progress(progress)
    return progress


def mark_lesson_completed(
    course_id: str,
    lesson_id: str,
    user_id: str = "default_user"
) -> CourseProgress:
    """Mark a lesson as completed."""
    progress = get_or_create_progress(course_id, user_id)
    if lesson_id not in progress.completed_lessons:
        progress.completed_lessons.append(lesson_id)
    
    # Recalculate overall progress
    course = load_course(course_id)
    if course:
        total_lessons = sum(len(m.lessons) for m in course.modules)
        completed_count = len(progress.completed_lessons)
        progress.overall_progress = (completed_count / total_lessons * 100) if total_lessons > 0 else 0
    
    save_progress(progress)
    return progress


# ============== Feedback & Version Storage ==============

def save_feedback(
    course_id: str,
    feedback_type: str,
    module_id: Optional[str],
    lesson_id: Optional[str],
    comments: Optional[str],
    original_content: dict,
    regenerated_content: dict
) -> bool:
    """
    Save feedback and version history for regenerated content.
    
    This maintains a history of all regenerations for potential rollback
    and analysis of what content works best.
    """
    ensure_storage_exists()
    try:
        # Save feedback log
        feedback_file = STORAGE_DIR / "feedback" / f"{course_id}_feedback.json"
        
        feedback_log = []
        if feedback_file.exists():
            with open(feedback_file, 'r', encoding='utf-8') as f:
                feedback_log = json.load(f)
        
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "feedback_type": feedback_type,
            "module_id": module_id,
            "lesson_id": lesson_id,
            "comments": comments
        }
        feedback_log.append(feedback_entry)
        
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedback_log, f, indent=2)
        
        # Save version history
        version_file = STORAGE_DIR / "versions" / f"{course_id}_versions.json"
        
        versions = []
        if version_file.exists():
            with open(version_file, 'r', encoding='utf-8') as f:
                versions = json.load(f)
        
        version_entry = {
            "timestamp": datetime.now().isoformat(),
            "module_id": module_id,
            "lesson_id": lesson_id,
            "original": original_content,
            "regenerated": regenerated_content
        }
        versions.append(version_entry)
        
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(versions, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return False


def get_feedback_history(course_id: str) -> List[dict]:
    """Get all feedback entries for a course"""
    ensure_storage_exists()
    try:
        feedback_file = STORAGE_DIR / "feedback" / f"{course_id}_feedback.json"
        if not feedback_file.exists():
            return []
        with open(feedback_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading feedback: {e}")
        return []


# ============ Quiz Attempt Memory Storage ============

def save_quiz_attempt_memory(memory: QuizAttemptMemory) -> bool:
    """Save quiz attempt memory to persistent storage"""
    ensure_storage_exists()
    try:
        # File path: quiz_memory/{course_id}_{lesson_id}_{user_id}.json
        memory_file = STORAGE_DIR / "quiz_memory" / f"{memory.course_id}_{memory.lesson_id}_{memory.user_id}.json"
        
        # Load existing attempts or create new list
        attempts = []
        if memory_file.exists():
            with open(memory_file, 'r', encoding='utf-8') as f:
                attempts = json.load(f)
        
        # Convert memory to dict for JSON storage
        memory_dict = {
            "attempt_id": memory.attempt_id,
            "user_id": memory.user_id,
            "course_id": memory.course_id,
            "lesson_id": memory.lesson_id,
            "initial_bloom_level": memory.initial_bloom_level,
            "final_bloom_level": memory.final_bloom_level,
            "feedback_entries": memory.feedback_entries,
            "too_difficult_count": memory.too_difficult_count,
            "concept_unclear_count": memory.concept_unclear_count,
            "need_more_examples_count": memory.need_more_examples_count,
            "wrong_questions": memory.wrong_questions,
            "recommended_bloom_level": memory.recommended_bloom_level,
            "adaptation_strategy": memory.adaptation_strategy,
            "created_at": memory.created_at,
            "completed": memory.completed
        }
        
        # Check if attempt already exists (update it) or add new
        existing_idx = next((i for i, a in enumerate(attempts) if a["attempt_id"] == memory.attempt_id), None)
        if existing_idx is not None:
            attempts[existing_idx] = memory_dict
        else:
            attempts.append(memory_dict)
        
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(attempts, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving quiz attempt memory: {e}")
        return False


def load_quiz_attempt_memory(course_id: str, lesson_id: str, user_id: str, attempt_id: str) -> Optional[QuizAttemptMemory]:
    """Load a specific quiz attempt memory"""
    ensure_storage_exists()
    try:
        memory_file = STORAGE_DIR / "quiz_memory" / f"{course_id}_{lesson_id}_{user_id}.json"
        if not memory_file.exists():
            return None
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            attempts = json.load(f)
        
        for attempt in attempts:
            if attempt["attempt_id"] == attempt_id:
                return QuizAttemptMemory(**attempt)
        
        return None
    except Exception as e:
        print(f"Error loading quiz attempt memory: {e}")
        return None


def get_latest_quiz_attempt_memory(course_id: str, lesson_id: str, user_id: str) -> Optional[QuizAttemptMemory]:
    """Get the most recent completed quiz attempt memory for a lesson"""
    ensure_storage_exists()
    try:
        memory_file = STORAGE_DIR / "quiz_memory" / f"{course_id}_{lesson_id}_{user_id}.json"
        if not memory_file.exists():
            return None
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            attempts = json.load(f)
        
        # Filter completed attempts and sort by created_at descending
        completed_attempts = [a for a in attempts if a.get("completed", False)]
        if not completed_attempts:
            return None
        
        # Sort by created_at (ISO format sorts correctly alphabetically)
        completed_attempts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return QuizAttemptMemory(**completed_attempts[0])
    except Exception as e:
        print(f"Error getting latest quiz attempt memory: {e}")
        return None


def get_all_quiz_attempts_for_lesson(course_id: str, lesson_id: str, user_id: str) -> List[QuizAttemptMemory]:
    """Get all quiz attempt memories for a lesson"""
    ensure_storage_exists()
    try:
        memory_file = STORAGE_DIR / "quiz_memory" / f"{course_id}_{lesson_id}_{user_id}.json"
        if not memory_file.exists():
            return []
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            attempts = json.load(f)
        
        return [QuizAttemptMemory(**a) for a in attempts]
    except Exception as e:
        print(f"Error getting quiz attempts: {e}")
        return []
