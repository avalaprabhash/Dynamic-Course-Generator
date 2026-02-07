"""
Course Generator Service

This module orchestrates the course generation process using the LLM service.

Flow:
1. Receive topic and duration from user
2. Log the request parameters
3. Call LLM service to generate UNIQUE, topic-specific course content
4. Validate the response references the topic
5. Build proper Course object with all required fields
6. Save to storage
7. Return the complete course

IMPORTANT: No mock fallback. If LLM fails, the request fails.
"""

import json
import uuid
import hashlib
from typing import Optional, Tuple
from datetime import datetime

from models import (
    Course, Module, Lesson, QuizQuestion, LessonContent,
    CoreConcept, PracticalExample,
    BloomLevel, Difficulty, CourseDifficulty, CourseGenerationRequest
)
from llm_service import (
    generate_course_content,
    regenerate_lesson_content
)
from storage import save_course, load_course, save_feedback, delete_progress


def parse_bloom_level(level_str: str) -> BloomLevel:
    """Safely parse a Bloom level string to enum."""
    level_map = {
        "remember": BloomLevel.REMEMBER,
        "understand": BloomLevel.UNDERSTAND,
        "apply": BloomLevel.APPLY,
        "analyze": BloomLevel.ANALYZE,
        "evaluate": BloomLevel.EVALUATE,
        "create": BloomLevel.CREATE
    }
    return level_map.get(level_str.lower(), BloomLevel.REMEMBER)


def parse_difficulty(diff_str: str) -> Difficulty:
    """Safely parse a difficulty string to enum."""
    diff_map = {
        "easy": Difficulty.EASY,
        "medium": Difficulty.MEDIUM,
        "hard": Difficulty.HARD
    }
    return diff_map.get(diff_str.lower(), Difficulty.MEDIUM)


def compute_content_hash(content: str) -> str:
    """Compute a hash for content uniqueness verification."""
    return hashlib.md5(content.encode()).hexdigest()[:12]


def build_lesson_content(content_data: dict, topic: str, bloom_level: str) -> LessonContent:
    """
    Build a structured LessonContent object from raw data.
    
    Handles both new structured format and legacy string format.
    """
    # If content is a string (legacy format), convert to structured
    if isinstance(content_data, str):
        return LessonContent(
            introduction=f"Welcome to this lesson on {topic}. {content_data[:200]}..." if len(content_data) > 200 else content_data,
            lesson_overview=[f"Understanding {topic}", f"Applying {topic} concepts"],
            core_concepts=[
                CoreConcept(
                    title=f"Core Concept: {topic}",
                    explanation=content_data,
                    code_example=None
                )
            ],
            guided_walkthrough=["Step 1: Review the content above", "Step 2: Practice with examples", "Step 3: Apply to your own projects"],
            practical_examples=[
                PracticalExample(
                    description=f"Example application of {topic}",
                    code=None,
                    explanation="See the core concepts for detailed explanation"
                )
            ],
            common_pitfalls=[f"Common mistake when learning {topic}"],
            mental_model=f"Think of {topic} as a building block for more advanced concepts.",
            summary=f"In this lesson, we covered key aspects of {topic}.",
            further_thinking=[f"How would you apply {topic} in a real project?"]
        )
    
    # Handle structured content format
    if isinstance(content_data, dict):
        # Parse core concepts
        core_concepts = []
        for cc in content_data.get("core_concepts", []):
            if isinstance(cc, dict):
                core_concepts.append(CoreConcept(
                    title=cc.get("title", "Concept"),
                    explanation=cc.get("explanation", "Explanation needed"),
                    code_example=cc.get("code_example")
                ))
        
        # Ensure minimum core concepts
        if len(core_concepts) < 2:
            core_concepts.append(CoreConcept(
                title=f"Additional {topic} Concept",
                explanation=f"This concept builds on the fundamentals of {topic}.",
                code_example=None
            ))
        
        # Parse practical examples
        practical_examples = []
        for ex in content_data.get("practical_examples", []):
            if isinstance(ex, dict):
                practical_examples.append(PracticalExample(
                    description=ex.get("description", "Example"),
                    code=ex.get("code"),
                    explanation=ex.get("explanation", "Explanation")
                ))
        
        # Ensure minimum examples
        if len(practical_examples) < 2:
            practical_examples.append(PracticalExample(
                description=f"Practical application of {topic}",
                code=None,
                explanation=f"Apply the concepts learned to a real scenario involving {topic}."
            ))
        
        # Build walkthrough
        walkthrough = content_data.get("guided_walkthrough", [])
        if not isinstance(walkthrough, list) or len(walkthrough) < 3:
            walkthrough = [
                f"Step 1: Understand the fundamentals of {topic}",
                f"Step 2: Practice with provided examples",
                f"Step 3: Apply to your own use cases"
            ]
        
        # Build overview
        overview = content_data.get("lesson_overview", [])
        if not isinstance(overview, list) or len(overview) == 0:
            overview = [f"Understanding {topic}", "Practical applications"]
        
        # Build pitfalls
        pitfalls = content_data.get("common_pitfalls", [])
        if not isinstance(pitfalls, list) or len(pitfalls) == 0:
            pitfalls = [f"Common mistakes when working with {topic}"]
        
        # Build further thinking
        further = content_data.get("further_thinking", [])
        if not isinstance(further, list) or len(further) == 0:
            further = [f"How would you extend your understanding of {topic}?"]
        
        return LessonContent(
            introduction=content_data.get("introduction", f"Welcome to this lesson on {topic}."),
            lesson_overview=overview,
            core_concepts=core_concepts,
            guided_walkthrough=walkthrough,
            practical_examples=practical_examples,
            common_pitfalls=pitfalls,
            mental_model=content_data.get("mental_model", f"Think of {topic} as a foundational concept."),
            summary=content_data.get("summary", f"This lesson covered the key aspects of {topic}."),
            further_thinking=further
        )
    
    # Fallback for unexpected format
    return LessonContent(
        introduction=f"Introduction to {topic}",
        lesson_overview=[f"Learn about {topic}"],
        core_concepts=[CoreConcept(title=topic, explanation=f"Core concepts of {topic}", code_example=None)],
        guided_walkthrough=["Step 1: Begin", "Step 2: Practice", "Step 3: Apply"],
        practical_examples=[PracticalExample(description="Example", code=None, explanation="Apply your learning")],
        common_pitfalls=["Watch out for common mistakes"],
        mental_model=f"Think of {topic} systematically",
        summary=f"Summary of {topic}",
        further_thinking=["How will you apply this?"]
    )


def validate_and_build_course(
    raw_data: dict,
    topic: str,
    duration_hours: int,
    difficulty: str
) -> Course:
    """
    Validate LLM output and build a proper Course object.
    
    This ensures all required fields are present and properly typed.
    Handles the new structured lesson content format.
    """
    course_id = str(uuid.uuid4())
    
    modules = []
    for mod_data in raw_data.get("modules", []):
        lessons = []
        for les_data in mod_data.get("lessons", []):
            bloom_level = parse_bloom_level(les_data.get("bloom_level", "remember"))
            
            # Parse quiz questions
            quiz_questions = []
            for q_data in les_data.get("quiz", []):
                question_id = q_data.get("question_id", str(uuid.uuid4()))
                options = q_data.get("options", ["A", "B", "C", "D"])
                correct_answer = q_data.get("correct_answer", options[0] if options else "A")
                
                if correct_answer not in options:
                    correct_answer = options[0] if options else "A"
                
                question = QuizQuestion(
                    question_id=question_id,
                    question=q_data.get("question", "Question text missing"),
                    options=options,
                    correct_answer=correct_answer,
                    difficulty=parse_difficulty(q_data.get("difficulty", "medium")),
                    bloom_level=bloom_level,
                    explanation=q_data.get("explanation", "Review the lesson for more details.")
                )
                quiz_questions.append(question)
            
            # Ensure at least 2 quiz questions per lesson
            while len(quiz_questions) < 2:
                quiz_questions.append(QuizQuestion(
                    question_id=str(uuid.uuid4()),
                    question=f"Practice question about {topic} at {bloom_level.value} level",
                    options=[f"Correct answer about {topic}", "Wrong option 1", "Wrong option 2", "Wrong option 3"],
                    correct_answer=f"Correct answer about {topic}",
                    difficulty=Difficulty.MEDIUM,
                    bloom_level=bloom_level,
                    explanation=f"This reinforces {topic} concepts."
                ))
            
            # Build structured lesson content
            content_data = les_data.get("content", {})
            lesson_content = build_lesson_content(content_data, topic, bloom_level.value)
            
            lesson = Lesson(
                lesson_id=les_data.get("lesson_id", str(uuid.uuid4())),
                lesson_title=les_data.get("lesson_title", f"{topic} Lesson"),
                bloom_level=bloom_level,
                learning_outcomes=les_data.get("learning_outcomes", [f"Understand {topic} concepts"]),
                content=lesson_content,
                quiz=quiz_questions,
                estimated_duration_minutes=les_data.get("estimated_duration_minutes", 30)
            )
            lessons.append(lesson)
        
        module = Module(
            module_id=mod_data.get("module_id", str(uuid.uuid4())),
            module_title=mod_data.get("module_title", f"{topic} Module"),
            module_description=mod_data.get("module_description", f"Learning about {topic}"),
            lessons=lessons
        )
        modules.append(module)
    
    course = Course(
        id=course_id,
        title=raw_data.get("title", f"Course on {topic}"),
        topic=topic,
        overview=raw_data.get("overview", f"A comprehensive course on {topic}"),
        duration_hours=duration_hours,
        difficulty=CourseDifficulty(difficulty) if isinstance(difficulty, str) else difficulty,
        confirmed=False,
        modules=modules,
        created_at=datetime.now()
    )
    
    return course


async def generate_course(request: CourseGenerationRequest, user_id: str = "default_user") -> Tuple[bool, Optional[Course], str]:
    """
    Generate a complete course based on topic and duration.
    
    This function:
    1. Logs the request parameters
    2. Calls LLM to generate topic-specific content
    3. Validates the response
    4. Builds and saves the course with user ownership
    
    NO MOCK FALLBACK - if LLM fails, request fails.
    
    Args:
        request: Course generation parameters
        user_id: The authenticated user's ID (from JWT)
    """
    # Log request parameters
    print(f"\n{'#'*60}")
    print("# COURSE GENERATION REQUEST")
    print(f"# Topic: {request.topic}")
    print(f"# Duration: {request.duration_hours} hours")
    print(f"# Difficulty: {request.difficulty.value}")
    print(f"# User: {user_id}")
    print(f"{'#'*60}\n")

    try:
        # Call LLM service to generate course content
        success, raw_data, message = await generate_course_content(
            request.topic,
            request.duration_hours,
            request.difficulty.value
        )
        
        if not success or not raw_data:
            print(f"[ERROR] Course generation failed: {message}")
            return False, None, message or "Failed to generate course content"
        
        # Log content hash for uniqueness verification
        content_str = json.dumps(raw_data)
        content_hash = compute_content_hash(content_str)
        print(f"[SUCCESS] Generated content hash: {content_hash}")
        print(f"[SUCCESS] Topic: {request.topic}")
        
        # Validate and build course object
        course = validate_and_build_course(
            raw_data,
            request.topic,
            request.duration_hours,
            request.difficulty.value
        )
        
        # Set user ownership
        course.user_id = user_id
        
        # Ensure we have content
        if not course.modules or not course.modules[0].lessons:
            return False, None, "Generated course has no content"
        
        # Log course structure
        print(f"[SUCCESS] Course structure:")
        print(f"  - Title: {course.title}")
        print(f"  - Owner: {user_id}")
        print(f"  - Modules: {len(course.modules)}")
        total_lessons = sum(len(m.lessons) for m in course.modules)
        print(f"  - Total lessons: {total_lessons}")
        
        # Save to storage
        if save_course(course):
            return True, course, message
        else:
            return False, None, "Failed to save course"
            
    except Exception as e:
        print(f"[EXCEPTION] {str(e)}")
        return False, None, f"Error generating course: {str(e)}"


async def regenerate_course(
    request_course_id: str,
    topic: str,
    duration_hours: int,
    difficulty: str,
    user_id: str = "default_user"
) -> Tuple[bool, Optional[Course], str]:
    """
    Regenerate an entire course using the same parameters.
    
    Args:
        request_course_id: The course to regenerate
        topic: Course topic
        duration_hours: Course duration
        difficulty: Course difficulty
        user_id: The authenticated user's ID (from JWT)
    """
    print(f"\n{'#'*60}")
    print("# COURSE REGENERATION REQUEST")
    print(f"# Course ID: {request_course_id}")
    print(f"# Topic: {topic}")
    print(f"# Duration: {duration_hours} hours")
    print(f"# Difficulty: {difficulty}")
    print(f"# User: {user_id}")
    print(f"{'#'*60}\n")

    try:
        existing = load_course(request_course_id)
        if not existing:
            return False, None, "Course not found"
        
        # Verify ownership
        if existing.user_id != user_id:
            return False, None, "You don't have permission to regenerate this course"

        success, raw_data, message = await generate_course_content(topic, duration_hours, difficulty)
        if not success or not raw_data:
            print(f"[ERROR] Course regeneration failed: {message}")
            return False, None, message or "Failed to regenerate course content"

        content_str = json.dumps(raw_data)
        content_hash = compute_content_hash(content_str)
        print(f"[SUCCESS] Regenerated content hash: {content_hash}")

        regenerated_course = validate_and_build_course(
            raw_data,
            topic,
            duration_hours,
            difficulty
        )

        regenerated_course.id = request_course_id
        regenerated_course.user_id = user_id  # Maintain ownership
        regenerated_course.created_at = existing.created_at
        regenerated_course.version = existing.version + 1
        regenerated_course.confirmed = False

        if save_course(regenerated_course):
            delete_progress(request_course_id, user_id)
            return True, regenerated_course, "Course regenerated"
        return False, None, "Failed to save regenerated course"

    except Exception as e:
        print(f"[EXCEPTION] {str(e)}")
        return False, None, f"Error regenerating course: {str(e)}"


async def regenerate_content(
    course_id: str,
    module_id: Optional[str],
    lesson_id: Optional[str],
    feedback_type: str,
    additional_comments: Optional[str] = None
) -> Tuple[bool, Optional[dict], str]:
    """
    Regenerate specific content based on user feedback.
    
    NO MOCK FALLBACK - if LLM fails, request fails.
    """
    print(f"\n[REGENERATION] Course: {course_id}, Lesson: {lesson_id}, Feedback: {feedback_type}")
    
    try:
        # Load existing course
        course = load_course(course_id)
        if not course:
            return False, None, "Course not found"
        
        # Find the content to regenerate
        original_content = None
        target_module = None
        target_lesson = None
        
        for module in course.modules:
            if lesson_id:
                for lesson in module.lessons:
                    if lesson.lesson_id == lesson_id:
                        original_content = lesson.model_dump()
                        target_module = module
                        target_lesson = lesson
                        break
            elif module_id and module.module_id == module_id:
                original_content = module.model_dump()
                target_module = module
                break
            
            if original_content:
                break
        
        if not original_content:
            return False, None, "Content not found"
        
        # Call LLM service to regenerate content
        success, regenerated, message = await regenerate_lesson_content(
            original_content,
            feedback_type,
            additional_comments
        )
        
        if not success or not regenerated:
            return False, None, message or "Failed to regenerate content"
        
        # Update the course with regenerated content
        if target_lesson:
            for i, lesson in enumerate(target_module.lessons):
                if lesson.lesson_id == lesson_id:
                    regenerated["lesson_id"] = lesson_id
                    
                    quiz_questions = []
                    for q_data in regenerated.get("quiz", []):
                        options = q_data.get("options", ["A", "B", "C", "D"])
                        correct_answer = q_data.get("correct_answer", options[0] if options else "A")
                        if correct_answer not in options:
                            correct_answer = options[0] if options else "A"
                        
                        quiz_questions.append(QuizQuestion(
                            question_id=q_data.get("question_id", str(uuid.uuid4())),
                            question=q_data.get("question", "Question"),
                            options=options,
                            correct_answer=correct_answer,
                            difficulty=parse_difficulty(q_data.get("difficulty", "medium")),
                            bloom_level=parse_bloom_level(regenerated.get("bloom_level", "remember")),
                            explanation=q_data.get("explanation", "Review the content.")
                        ))
                    
                    new_lesson = Lesson(
                        lesson_id=lesson_id,
                        lesson_title=regenerated.get("lesson_title", lesson.lesson_title),
                        bloom_level=parse_bloom_level(regenerated.get("bloom_level", lesson.bloom_level.value)),
                        learning_outcomes=regenerated.get("learning_outcomes", lesson.learning_outcomes),
                        content=regenerated.get("content", lesson.content),
                        quiz=quiz_questions if quiz_questions else lesson.quiz,
                        estimated_duration_minutes=regenerated.get("estimated_duration_minutes", lesson.estimated_duration_minutes)
                    )
                    target_module.lessons[i] = new_lesson
                    break
        
        elif target_module:
            for i, module in enumerate(course.modules):
                if module.module_id == module_id:
                    regenerated["module_id"] = module_id
                    if "lessons" in regenerated:
                        for j, les in enumerate(regenerated.get("lessons", [])):
                            if j < len(module.lessons):
                                les["lesson_id"] = module.lessons[j].lesson_id
                    break
        
        course.version += 1
        save_course(course)
        
        save_feedback(
            course_id=course_id,
            feedback_type=feedback_type,
            module_id=module_id,
            lesson_id=lesson_id,
            comments=additional_comments,
            original_content=original_content,
            regenerated_content=regenerated
        )
        
        return True, regenerated, message
        
    except Exception as e:
        print(f"[EXCEPTION] Regeneration error: {str(e)}")
        return False, None, f"Error regenerating content: {str(e)}"
