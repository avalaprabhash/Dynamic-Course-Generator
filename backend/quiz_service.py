"""
Quiz Service - Clean Quiz Logic with Adaptive Difficulty

This module provides a streamlined quiz experience:
- Generate quizzes from lesson content using LLM
- Grade submissions and provide detailed feedback
- Adapt difficulty based on performance
- Track progress with Bloom's Taxonomy levels
"""

import uuid
from typing import List, Dict, Tuple, Optional
from pydantic import BaseModel
from datetime import datetime

from models import (
    QuizQuestion, QuizSubmission, QuizResult, Difficulty, 
    Course, BloomLevel
)
from storage import (
    load_course, load_progress, update_lesson_progress
)
from llm_service import generate_quiz_content


# ============== Constants ==============

# Score thresholds
PASS_THRESHOLD = 70.0  # Minimum score to pass
MASTERY_THRESHOLD = 85.0  # Score indicating mastery
STRUGGLING_THRESHOLD = 50.0  # Score indicating need for easier content

# Bloom's Taxonomy progression
BLOOM_LEVELS = [
    BloomLevel.REMEMBER,
    BloomLevel.UNDERSTAND,
    BloomLevel.APPLY,
    BloomLevel.ANALYZE,
    BloomLevel.EVALUATE,
    BloomLevel.CREATE
]


# ============== Pydantic Models ==============

class QuizGenerationRequest(BaseModel):
    """Request model for dynamic quiz generation"""
    course_id: str
    lesson_id: str
    difficulty: str = "medium"
    num_questions: int = 3


class GeneratedQuiz(BaseModel):
    """Response model for generated quiz"""
    lesson_id: str
    lesson_title: str
    bloom_level: str
    difficulty: str
    questions: List[dict]


# ============== Core Quiz Functions ==============

def grade_quiz(
    questions: List[QuizQuestion],
    answers: Dict[str, str]
) -> Tuple[float, int, int, List[dict]]:
    """
    Grade a quiz and provide detailed feedback.
    
    Args:
        questions: List of quiz questions
        answers: Dict mapping question_id to selected answer
        
    Returns:
        Tuple of (score, correct_count, total, feedback_list)
    """
    correct_count = 0
    total = len(questions)
    feedback = []
    
    for question in questions:
        user_answer = answers.get(question.question_id, "")
        is_correct = user_answer == question.correct_answer
        
        if is_correct:
            correct_count += 1
        
        feedback.append({
            "question_id": question.question_id,
            "question": question.question,
            "options": question.options,
            "user_answer": user_answer,
            "correct_answer": question.correct_answer,
            "is_correct": is_correct,
            "explanation": question.explanation or "Review the lesson content for more details.",
            "difficulty": question.difficulty.value,
            "bloom_level": question.bloom_level.value
        })
    
    score = (correct_count / total * 100) if total > 0 else 0
    return score, correct_count, total, feedback


def calculate_new_difficulty(current_difficulty: Difficulty, score: float) -> Difficulty:
    """
    Determine new difficulty based on quiz score.
    
    - Score >= 85%: Increase difficulty
    - Score < 50%: Decrease difficulty  
    - Otherwise: Stay the same
    """
    difficulty_order = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
    current_index = difficulty_order.index(current_difficulty)
    
    if score >= MASTERY_THRESHOLD:
        # Great performance - increase difficulty
        if current_index < len(difficulty_order) - 1:
            return difficulty_order[current_index + 1]
    elif score < STRUGGLING_THRESHOLD:
        # Struggling - decrease difficulty
        if current_index > 0:
            return difficulty_order[current_index - 1]
    
    return current_difficulty


def calculate_new_bloom_level(current_bloom: BloomLevel, score: float, passed: bool) -> BloomLevel:
    """
    Determine new Bloom level based on quiz performance.
    
    - Passed with >= 85%: Move up one level
    - Failed with < 50%: Move down one level
    - Otherwise: Stay the same
    """
    current_index = BLOOM_LEVELS.index(current_bloom)
    
    if passed and score >= MASTERY_THRESHOLD:
        # Excellent - move up
        if current_index < len(BLOOM_LEVELS) - 1:
            return BLOOM_LEVELS[current_index + 1]
    elif not passed and score < STRUGGLING_THRESHOLD:
        # Struggling - move down
        if current_index > 0:
            return BLOOM_LEVELS[current_index - 1]
    
    return current_bloom


def process_quiz_submission(submission: QuizSubmission, user_id: str = "default_user") -> Optional[QuizResult]:
    """
    Process a complete quiz submission.
    
    This is the main entry point for quiz grading:
    1. Load course and find the lesson
    2. Grade the submission
    3. Calculate new difficulty and Bloom level
    4. Update progress
    5. Return detailed results
    """
    course = load_course(submission.course_id)
    if not course:
        return None
    
    # Find the lesson
    target_lesson = None
    target_module_id = None
    for module in course.modules:
        for lesson in module.lessons:
            if lesson.lesson_id == submission.lesson_id:
                target_lesson = lesson
                target_module_id = module.module_id
                break
        if target_lesson:
            break
    
    if not target_lesson:
        return None
    
    # Get current progress
    progress = load_progress(submission.course_id, user_id)
    current_difficulty = Difficulty.MEDIUM
    current_bloom = target_lesson.bloom_level
    
    if progress and target_module_id in progress.modules:
        module_progress = progress.modules[target_module_id]
        if submission.lesson_id in module_progress.get("lessons", {}):
            lesson_progress = module_progress["lessons"][submission.lesson_id]
            current_difficulty = Difficulty(lesson_progress.get("current_difficulty", "medium"))
            current_bloom = BloomLevel(lesson_progress.get("current_bloom_level", target_lesson.bloom_level.value))
    
    # Grade the quiz
    score, correct_count, total, feedback = grade_quiz(
        target_lesson.quiz,
        submission.answers
    )
    
    passed = score >= PASS_THRESHOLD
    
    # Calculate new difficulty and bloom level
    new_difficulty = calculate_new_difficulty(current_difficulty, score)
    new_bloom = calculate_new_bloom_level(current_bloom, score, passed)
    
    # Update progress
    update_lesson_progress(
        course_id=submission.course_id,
        module_id=target_module_id,
        lesson_id=submission.lesson_id,
        score=score,
        new_difficulty=new_difficulty,
        smoothed_score=score / 100,
        bloom_level=new_bloom,
        user_id=user_id
    )
    
    return QuizResult(
        course_id=submission.course_id,
        lesson_id=submission.lesson_id,
        score=score,
        correct_count=correct_count,
        total_questions=total,
        passed=passed,
        needs_feedback=correct_count < total,  # Show feedback if any wrong answers
        updated_difficulty=new_difficulty,
        current_bloom_level=current_bloom,
        next_bloom_level=new_bloom,
        feedback=feedback
    )


# ============== Quiz Generation ==============

async def generate_quiz_for_lesson(
    course_id: str,
    lesson_id: str,
    difficulty: str = "medium",
    num_questions: int = 3,
    bloom_level: str = None
) -> Tuple[bool, Optional[dict], str]:
    """
    Generate a new quiz for a lesson using LLM.
    
    Args:
        course_id: The course containing the lesson
        lesson_id: The lesson to generate quiz for
        difficulty: Desired difficulty (easy, medium, hard)
        num_questions: Number of questions to generate
        bloom_level: Optional Bloom level override
        
    Returns:
        Tuple of (success, quiz_data, message)
    """
    course = load_course(course_id)
    if not course:
        return False, None, "Course not found"
    
    # Find the lesson
    target_lesson = None
    for module in course.modules:
        for lesson in module.lessons:
            if lesson.lesson_id == lesson_id:
                target_lesson = lesson
                break
        if target_lesson:
            break
    
    if not target_lesson:
        return False, None, "Lesson not found"
    
    # Use provided bloom level or lesson's default
    target_bloom = bloom_level or target_lesson.bloom_level.value
    
    # Generate quiz using LLM
    success, quiz_data, message = await generate_quiz_content(
        lesson_content=target_lesson.content,
        bloom_level=target_bloom,
        difficulty=difficulty,
        num_questions=num_questions
    )
    
    if not success or not quiz_data:
        return False, None, message or "Failed to generate quiz"
    
    # Add IDs and normalize
    for q in quiz_data:
        if "question_id" not in q:
            q["question_id"] = str(uuid.uuid4())
        q["bloom_level"] = target_bloom
        q["difficulty"] = difficulty
    
    result = {
        "lesson_id": lesson_id,
        "lesson_title": target_lesson.lesson_title,
        "bloom_level": target_bloom,
        "difficulty": difficulty,
        "questions": quiz_data
    }
    
    return True, result, "Quiz generated successfully"


async def generate_retake_quiz(
    course_id: str,
    lesson_id: str,
    user_id: str,
    num_questions: int = 3
) -> Tuple[bool, Optional[dict], str]:
    """
    Generate a quiz for retake, potentially with adjusted difficulty/bloom level.
    
    Checks previous progress and adjusts accordingly:
    - If struggling (low scores): Lower difficulty and Bloom level
    - If doing well: Maintain or increase
    """
    course = load_course(course_id)
    if not course:
        return False, None, "Course not found"
    
    # Find lesson and module
    target_lesson = None
    target_module_id = None
    for module in course.modules:
        for lesson in module.lessons:
            if lesson.lesson_id == lesson_id:
                target_lesson = lesson
                target_module_id = module.module_id
                break
        if target_lesson:
            break
    
    if not target_lesson:
        return False, None, "Lesson not found"
    
    # Get current progress to determine adaptation
    progress = load_progress(course_id, user_id)
    difficulty = "medium"
    bloom_level = target_lesson.bloom_level.value
    
    if progress and target_module_id in progress.modules:
        module_progress = progress.modules[target_module_id]
        if lesson_id in module_progress.get("lessons", {}):
            lesson_progress = module_progress["lessons"][lesson_id]
            difficulty = lesson_progress.get("current_difficulty", "medium")
            bloom_level = lesson_progress.get("current_bloom_level", target_lesson.bloom_level.value)
    
    # Generate the quiz
    return await generate_quiz_for_lesson(
        course_id=course_id,
        lesson_id=lesson_id,
        difficulty=difficulty,
        num_questions=num_questions,
        bloom_level=bloom_level
    )


# ============== Mastery Calculation ==============

def calculate_mastery_level(best_score: float, quiz_attempts: int) -> dict:
    """
    Calculate a human-readable mastery level for display.
    
    Returns dict with level name, description, and color for UI.
    """
    if quiz_attempts == 0:
        return {
            "level": "Not Started",
            "description": "Take the quiz to assess your knowledge",
            "color": "gray",
            "score": 0
        }
    
    if best_score >= 85:
        return {
            "level": "Mastered",
            "description": "Excellent! You've mastered this content",
            "color": "emerald",
            "score": best_score
        }
    elif best_score >= 70:
        return {
            "level": "Proficient",
            "description": "Good understanding, keep it up!",
            "color": "blue",
            "score": best_score
        }
    elif best_score >= 50:
        return {
            "level": "Developing",
            "description": "Making progress, review the material",
            "color": "amber",
            "score": best_score
        }
    else:
        return {
            "level": "Needs Practice",
            "description": "Review the lesson and try again",
            "color": "rose",
            "score": best_score
        }


# ============== Helper Functions ==============

def get_bloom_level_description(level: BloomLevel) -> str:
    """Get a description for a Bloom's Taxonomy level."""
    descriptions = {
        BloomLevel.REMEMBER: "Recall facts and basic concepts",
        BloomLevel.UNDERSTAND: "Explain ideas and concepts",
        BloomLevel.APPLY: "Use information in new situations",
        BloomLevel.ANALYZE: "Draw connections among ideas",
        BloomLevel.EVALUATE: "Justify decisions and actions",
        BloomLevel.CREATE: "Produce new or original work"
    }
    return descriptions.get(level, "")


def get_difficulty_description(difficulty: Difficulty) -> str:
    """Get a description for a difficulty level."""
    descriptions = {
        Difficulty.EASY: "Foundational questions to build confidence",
        Difficulty.MEDIUM: "Balanced questions testing core understanding",
        Difficulty.HARD: "Challenging questions requiring deep knowledge"
    }
    return descriptions.get(difficulty, "")
