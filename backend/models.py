"""
Data Models for the AI-Powered Course & Quiz Generator

This module defines all the data structures used throughout the application.
These models ensure type safety and validation using Pydantic.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime
import uuid


class BloomLevel(str, Enum):
    """
    Bloom's Taxonomy Cognitive Levels
    
    These represent the hierarchical levels of cognitive learning objectives,
    from basic recall (Remember) to complex creation (Create).
    """
    REMEMBER = "Remember"
    UNDERSTAND = "Understand"
    APPLY = "Apply"
    ANALYZE = "Analyze"
    EVALUATE = "Evaluate"
    CREATE = "Create"


class CourseDifficulty(str, Enum):
    """Course difficulty levels"""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class Difficulty(str, Enum):
    """Quiz question difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuizQuestion(BaseModel):
    """
    A single quiz question with multiple choice options.
    
    Each question is aligned with a Bloom's Taxonomy level and has
    an associated difficulty that can adapt based on learner performance.
    """
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    options: List[str] = Field(min_length=2, max_length=6)
    correct_answer: str
    difficulty: Difficulty = Difficulty.MEDIUM
    bloom_level: BloomLevel = BloomLevel.REMEMBER
    explanation: Optional[str] = None


# ============== Structured Lesson Content Models ==============

class CoreConcept(BaseModel):
    """A single core concept with explanation and optional code example."""
    title: str
    explanation: str  # 2-3 paragraphs
    code_example: Optional[str] = None


class PracticalExample(BaseModel):
    """A practical real-world or programming example."""
    description: str
    code: Optional[str] = None
    explanation: str


class LessonContent(BaseModel):
    """
    Structured lesson content following professional course standards.
    
    Each lesson is a comprehensive learning document with multiple sections,
    designed to be read like a textbook chapter or tutorial.
    """
    introduction: str  # 1-2 paragraphs setting context
    lesson_overview: List[str]  # Bullet points of what will be covered
    core_concepts: List[CoreConcept]  # Main body - multiple subsections
    guided_walkthrough: List[str]  # Step-by-step explanation
    practical_examples: List[PracticalExample]  # At least 2 examples
    common_pitfalls: List[str]  # Common mistakes and why they happen
    mental_model: str  # Analogies or visualization
    summary: str  # Conceptual recap
    further_thinking: List[str]  # Reflective prompts (Bloom's aligned)


class Lesson(BaseModel):
    """
    A single lesson within a module.
    
    Contains comprehensive learning content aligned with a specific Bloom's Taxonomy level.
    The content is now a structured document rather than a simple text field.
    """
    lesson_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lesson_title: str
    bloom_level: BloomLevel
    learning_outcomes: List[str]
    content: LessonContent  # Structured content
    quiz: List[QuizQuestion] = []
    estimated_duration_minutes: int = 30  # Increased for comprehensive content


class Module(BaseModel):
    """
    A module groups related lessons together.
    
    Modules represent major topic areas within a course and contain
    multiple lessons that progress through Bloom's Taxonomy levels.
    """
    module_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    module_title: str
    module_description: str
    lessons: List[Lesson] = []


class Course(BaseModel):
    """
    The complete course structure.
    
    A course contains multiple modules, each with lessons that cover
    different aspects of the topic at various cognitive levels.
    Each course belongs to a specific user (user_id from JWT).
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default_user"  # Owner of the course (from JWT)
    title: str
    topic: str
    overview: str
    duration_hours: int
    difficulty: CourseDifficulty = CourseDifficulty.INTERMEDIATE
    confirmed: bool = False
    modules: List[Module] = []
    created_at: datetime = Field(default_factory=datetime.now)
    version: int = 1


# Request/Response Models

class CourseGenerationRequest(BaseModel):
    """Request model for generating a new course"""
    topic: str = Field(min_length=3, max_length=200, description="The subject to create a course about")
    duration_hours: int = Field(ge=1, le=100, description="Target course duration in hours")
    difficulty: CourseDifficulty = Field(default=CourseDifficulty.INTERMEDIATE, description="Target difficulty level")


class CourseGenerationResponse(BaseModel):
    """Response model after course generation"""
    success: bool
    course: Optional[Course] = None
    message: str


class RegenerateCourseRequest(BaseModel):
    """Request model for regenerating an entire course"""
    course_id: str
    topic: str = Field(min_length=3, max_length=200)
    duration_hours: int = Field(ge=1, le=100)
    difficulty: CourseDifficulty = CourseDifficulty.INTERMEDIATE


class QuizAttemptFeedback(str, Enum):
    """Feedback options shown after a failed quiz attempt (score < 70%)"""
    TOO_DIFFICULT = "Too difficult"
    CONCEPT_UNCLEAR = "Concept unclear"
    NEED_MORE_EXAMPLES = "Need more examples"
    OKAY_CONTINUE = "Okay, can continue"


class WrongAnswerFeedback(str, Enum):
    """Feedback options shown immediately after a wrong answer during quiz"""
    TOO_DIFFICULT = "Too difficult"
    CONCEPT_UNCLEAR = "Concept unclear"
    NEED_MORE_EXAMPLES = "Need more examples"


class WrongAnswerFeedbackRequest(BaseModel):
    """Request to submit feedback after getting a question wrong"""
    course_id: str
    lesson_id: str
    question_id: str
    feedback: WrongAnswerFeedback


class QuizSubmission(BaseModel):
    """User's answers to a quiz"""
    course_id: str
    lesson_id: str
    answers: dict  # question_id -> selected_answer


class QuizAttemptFeedbackRequest(BaseModel):
    """Request to submit feedback after a quiz attempt"""
    course_id: str
    lesson_id: str
    feedback: QuizAttemptFeedback


class QuizResult(BaseModel):
    """Result of a quiz submission"""
    course_id: str
    lesson_id: str
    score: float  # Percentage 0-100
    correct_count: int
    total_questions: int
    passed: bool  # True if score >= 70%
    needs_feedback: bool = False  # True if score < 70% and feedback should be requested
    updated_difficulty: Difficulty
    current_bloom_level: BloomLevel
    next_bloom_level: Optional[BloomLevel] = None
    feedback: List[dict]  # Per-question feedback (correct/incorrect details)
    timestamp: datetime = Field(default_factory=datetime.now)


class FeedbackType(str, Enum):
    """Types of user feedback for content regeneration"""
    TOO_EASY = "too_easy"
    TOO_HARD = "too_hard"
    UNCLEAR = "unclear"
    MORE_EXAMPLES = "more_examples"
    DIFFERENT_APPROACH = "different_approach"


class FeedbackRequest(BaseModel):
    """User feedback for content regeneration"""
    course_id: str
    module_id: Optional[str] = None
    lesson_id: Optional[str] = None
    feedback_type: FeedbackType
    additional_comments: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Response after processing feedback"""
    success: bool
    message: str
    regenerated_content: Optional[dict] = None


# Progress Tracking Models

class QuizAttempt(BaseModel):
    """Record of a single quiz attempt"""
    attempt_number: int
    score: float
    passed: bool
    feedback: Optional[QuizAttemptFeedback] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class LessonProgress(BaseModel):
    """Progress for a single lesson"""
    lesson_id: str
    completed: bool = False
    quiz_attempts: int = 0
    best_score: float = 0.0
    current_difficulty: Difficulty = Difficulty.MEDIUM
    current_bloom_level: BloomLevel = BloomLevel.REMEMBER
    smoothed_score: float = 0.5  # For adaptive difficulty (0-1 scale)
    attempt_history: List[QuizAttempt] = []  # Track all attempts with feedback


class ModuleProgress(BaseModel):
    """Progress for a module"""
    module_id: str
    lessons: dict = {}  # lesson_id -> LessonProgress


class CourseProgress(BaseModel):
    """Complete progress tracking for a course"""
    course_id: str
    user_id: str = "default_user"
    current_module_index: int = 0
    current_lesson_index: int = 0
    completed_lessons: List[str] = []  # List of lesson_ids
    modules: dict = {}  # module_id -> ModuleProgress
    overall_progress: float = 0.0  # Percentage complete
    started_at: datetime = Field(default_factory=datetime.now)
    last_accessed_at: datetime = Field(default_factory=datetime.now)


class ProgressUpdate(BaseModel):
    """Response when progress is updated"""
    course_id: str
    lesson_id: str
    new_progress: float
    current_difficulty: Difficulty
    message: str


class LessonAccessRequest(BaseModel):
    """Request to track lesson access"""
    course_id: str
    module_index: int
    lesson_index: int
    lesson_id: str


class QuizAttemptMemory(BaseModel):
    """Stores feedback from a quiz attempt for adaptive regeneration"""
    attempt_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    course_id: str
    lesson_id: str
    initial_bloom_level: str
    final_bloom_level: str
    feedback_entries: List[dict] = []  # List of {question_id, feedback_type, bloom_level}
    too_difficult_count: int = 0
    concept_unclear_count: int = 0
    need_more_examples_count: int = 0
    wrong_questions: List[dict] = []  # Questions user got wrong
    recommended_bloom_level: Optional[str] = None
    adaptation_strategy: Optional[str] = None  # "simplify" | "add_examples" | "lower_level"
    created_at: datetime = Field(default_factory=datetime.now)
    completed: bool = False


class QuizRetakeRequest(BaseModel):
    """Request to retake a quiz with adapted difficulty"""
    course_id: str
    lesson_id: str
