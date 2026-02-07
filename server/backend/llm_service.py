"""
LLM Service - Real AI Integration Layer (Perplexity API)

This module handles all interactions with the Perplexity LLM API.
It generates STRUCTURED, GUIDE-LIKE educational content with:
- Strong topic-aware prompts that ensure unique content
- Bloom's Taxonomy aware tone and structure
- Strict JSON output validation
- Content relevance validation
- NO fallback to mock data
"""

import os
import json
import uuid
import hashlib
from typing import Optional, Dict, Any, List, Tuple
from dotenv import load_dotenv
from openai import AsyncOpenAI, APIError, APIConnectionError, RateLimitError

# Load environment variables (override system defaults)
load_dotenv(override=True)

# Configuration
USE_MOCK = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
# Use specific key name to avoid conflicts with global OPENAI_API_KEY
OPENAI_API_KEY = os.getenv("PERPLEXITY_API_KEY") or os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.perplexity.ai")
MODEL_NAME = os.getenv("LLM_MODEL", "sonar")
TEMPERATURE = 0.7
MAX_TOKENS = 8000
MAX_RETRIES = 3

# System prompt - professional course author
SYSTEM_PROMPT = """You are writing a professional programming course lesson.

CRITICAL RULES:
- Do NOT summarize. Write COMPREHENSIVE, DETAILED content.
- Do NOT write short answers. Each section must be substantial.
- Assume the learner is reading this as part of a multi-hour course.
- Depth and clarity matter more than brevity.

TEACHING STYLE:
- Write like a patient instructor explaining to a motivated beginner
- Use real-world analogies and practical examples
- Include code examples where relevant
- Explain the "why" behind concepts, not just the "what"

JSON OUTPUT RULES (CRITICAL):
- Output ONLY valid JSON - no text before or after
- No markdown code blocks around the JSON (no ```)
- All strings must be properly escaped for JSON
- Use \\n for newlines in strings, NOT actual line breaks
- Use \\\\ for backslashes in code examples
- Keep code examples SHORT and SIMPLE (under 5 lines)
- Avoid special characters that need escaping"""

# Stricter system prompt for retry attempts
STRICT_SYSTEM_PROMPT = """You are a professional course author. Output VALID JSON ONLY.

CRITICAL JSON RULES:
1. Output ONLY valid JSON - no text before or after
2. No markdown code blocks (no ```)
3. ALL strings must use proper JSON escaping
4. For newlines in strings: use \\n (escaped)
5. For backslashes: use \\\\ (double escaped)
6. Keep code examples VERY SHORT (3-5 lines max)
7. Avoid complex escape sequences
8. Test that your JSON is valid before outputting

CONTENT RULES:
1. Each lesson must be LONG-FORM and DETAILED
2. Core concepts: at least 2 detailed subsections
3. Guided walkthrough: at least 4 steps
4. Practical examples: at least 2 with explanations"""


# Bloom's Taxonomy with teaching approaches
BLOOM_LEVELS = {
    "Remember": {
        "description": "Recall facts and basic concepts",
        "teaching_approach": "Focus on definitions, key terms, and fundamental facts. Use memory aids and clear, simple explanations.",
        "content_style": "Define key terms clearly. List important facts. Use simple recall questions.",
        "verbs": ["define", "list", "name", "identify", "recall", "recognize"],
        "question_types": ["What is...", "List the...", "Name the...", "Which of..."]
    },
    "Understand": {
        "description": "Explain ideas or concepts",
        "teaching_approach": "Use analogies, comparisons, and explanations. Help learners grasp the 'why' behind concepts.",
        "content_style": "Explain with analogies. Compare and contrast. Use 'think of it like...' examples.",
        "verbs": ["explain", "describe", "summarize", "interpret", "classify"],
        "question_types": ["Explain why...", "What does X mean...", "Summarize...", "Compare..."]
    },
    "Apply": {
        "description": "Use information in new situations",
        "teaching_approach": "Provide step-by-step procedures, practical examples, and hands-on exercises.",
        "content_style": "Show step-by-step how to do something. Include code examples or procedures. Focus on 'how to'.",
        "verbs": ["apply", "demonstrate", "solve", "use", "implement"],
        "question_types": ["How would you use...", "Apply this to...", "Solve...", "Calculate..."]
    },
    "Analyze": {
        "description": "Draw connections among ideas",
        "teaching_approach": "Break down complex topics, compare components, and examine relationships.",
        "content_style": "Break down into components. Compare different approaches. Examine cause and effect.",
        "verbs": ["analyze", "differentiate", "examine", "compare", "contrast"],
        "question_types": ["Why does...", "What is the relationship...", "Analyze...", "What evidence..."]
    },
    "Evaluate": {
        "description": "Justify a decision or course of action",
        "teaching_approach": "Present pros/cons, criteria for judgment, and critical thinking frameworks.",
        "content_style": "Present pros and cons. Discuss trade-offs. Help learners form judgments with criteria.",
        "verbs": ["evaluate", "judge", "critique", "justify", "assess"],
        "question_types": ["Do you agree...", "What is the best...", "Evaluate...", "Judge..."]
    },
    "Create": {
        "description": "Produce new or original work",
        "teaching_approach": "Provide open-ended challenges, design tasks, and creative problem-solving.",
        "content_style": "Give open-ended challenges. Encourage design thinking. Focus on synthesis and creation.",
        "verbs": ["create", "design", "develop", "formulate", "propose"],
        "question_types": ["Design a...", "What would happen if...", "Create...", "Propose..."]
    }
}


def get_openai_client() -> AsyncOpenAI:
    """Create and return an AsyncOpenAI client configured for Perplexity."""
    if not OPENAI_API_KEY:
        print("[ERROR] OPENAI_API_KEY is missing or empty!")
    else:
        print(f"[INFO] Using API Key: {OPENAI_API_KEY[:5]}...{OPENAI_API_KEY[-4:]}")
        
    return AsyncOpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
        default_headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    )


def compute_content_hash(content: dict) -> str:
    """Compute a hash of the content for uniqueness verification."""
    content_str = json.dumps(content, sort_keys=True)
    return hashlib.md5(content_str.encode()).hexdigest()[:12]


def clean_json_response(response: str) -> str:
    """Clean LLM response to extract valid JSON."""
    import re
    
    cleaned = response.strip()
    
    # Remove BOM
    if cleaned.startswith('\ufeff'):
        cleaned = cleaned[1:]
    
    # Remove markdown code blocks
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    
    cleaned = cleaned.strip()
    
    # Fix common escape sequence issues in JSON strings
    # Replace invalid escape sequences with valid ones
    def fix_escapes(match):
        s = match.group(0)
        # Fix common problematic escapes
        s = s.replace('\\"', '"')  # Temporarily store escaped quotes
        s = s.replace('\\', '\\\\')  # Escape all backslashes
        s = s.replace('\\\\"', '\\"')  # Restore escaped quotes
        # Fix double-escaped sequences
        s = s.replace('\\\\n', '\\n')
        s = s.replace('\\\\t', '\\t')
        s = s.replace('\\\\r', '\\r')
        return s
    
    return cleaned


def fix_json_string(json_str: str) -> str:
    """Attempt to fix common JSON issues."""
    import re
    
    # Remove any control characters except valid whitespace
    json_str = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', json_str)
    
    # Try to fix unescaped newlines inside strings
    # This is a simplified approach - replace literal newlines in strings with \n
    lines = json_str.split('\n')
    fixed_lines = []
    in_string = False
    
    for i, line in enumerate(lines):
        # Count unescaped quotes to track string state
        quote_count = 0
        j = 0
        while j < len(line):
            if line[j] == '"' and (j == 0 or line[j-1] != '\\'):
                quote_count += 1
            j += 1
        
        if in_string and quote_count % 2 == 1:
            # We were in a string and this line closes it
            fixed_lines.append('\\n' + line)
            in_string = False
        elif in_string:
            # Still in string, this line is part of it
            fixed_lines.append('\\n' + line)
        else:
            # Not in string
            if i > 0:
                fixed_lines.append('\n' + line)
            else:
                fixed_lines.append(line)
            # Check if we end in an open string
            if quote_count % 2 == 1:
                in_string = True
    
    return ''.join(fixed_lines)


def repair_quiz_json(text: str) -> Optional[list]:
    """Aggressively try to extract quiz data from malformed response."""
    import re
    
    questions = []
    
    # Try to find question patterns even in broken JSON
    # Pattern for questions: "question": "..."
    # Split by common question boundaries
    
    # Remove markdown artifacts
    text = re.sub(r'```\w*\n?', '', text)
    text = text.replace('```', '')
    
    # Try to find JSON-like question objects
    # Look for patterns like {"question": "...", "options": [...], "correct_answer": "...", ...}
    
    q_pattern = r'"question"\s*:\s*"([^"]*(?:\\.[^"]*)*)"'
    opt_pattern = r'"options"\s*:\s*\[(.*?)\]'
    ans_pattern = r'"correct_answer"\s*:\s*"([^"]*(?:\\.[^"]*)*)"'
    exp_pattern = r'"explanation"\s*:\s*"([^"]*(?:\\.[^"]*)*)"'
    diff_pattern = r'"difficulty"\s*:\s*"([^"]*)"'
    
    # Split by likely question boundaries
    blocks = re.split(r'\}\s*,?\s*\{', text)
    
    for block in blocks:
        q_match = re.search(q_pattern, block)
        opt_match = re.search(opt_pattern, block, re.DOTALL)
        ans_match = re.search(ans_pattern, block)
        
        if q_match and opt_match and ans_match:
            options_str = opt_match.group(1)
            # Extract options - handle various quote styles
            options = re.findall(r'"([^"]*(?:\\.[^"]*)*)"', options_str)
            
            if len(options) >= 2:  # Need at least 2 options
                exp_match = re.search(exp_pattern, block)
                diff_match = re.search(diff_pattern, block)
                
                q_obj = {
                    "question": q_match.group(1).replace('\\"', '"').replace('\\n', '\n'),
                    "options": [opt.replace('\\"', '"') for opt in options],
                    "correct_answer": ans_match.group(1).replace('\\"', '"'),
                    "difficulty": diff_match.group(1) if diff_match else "medium",
                    "explanation": exp_match.group(1).replace('\\"', '"').replace('\\n', '\n') if exp_match else "No explanation provided."
                }
                
                # Validate correct_answer is in options
                if q_obj["correct_answer"] in q_obj["options"]:
                    questions.append(q_obj)
                else:
                    # Try case-insensitive match
                    for opt in q_obj["options"]:
                        if opt.lower().strip() == q_obj["correct_answer"].lower().strip():
                            q_obj["correct_answer"] = opt
                            questions.append(q_obj)
                            break
    
    return questions if questions else None


def validate_json(response: str) -> Tuple[bool, Optional[dict], str]:
    """Validate that a response is valid JSON with repair attempts."""
    cleaned = clean_json_response(response)
    
    # First try: direct parse
    try:
        data = json.loads(cleaned)
        return True, data, ""
    except json.JSONDecodeError as e:
        first_error = str(e)
    
    # Second try: fix common issues
    try:
        fixed = fix_json_string(cleaned)
        data = json.loads(fixed)
        return True, data, ""
    except json.JSONDecodeError:
        pass
    
    # Third try: use regex to extract JSON array (for quiz responses)
    try:
        import re
        # Try to find array first (common for quiz responses)
        array_match = re.search(r'\[[\s\S]*\]', cleaned)
        if array_match:
            extracted = array_match.group(0)
            data = json.loads(extracted)
            return True, data, ""
    except json.JSONDecodeError:
        pass
    
    # Fourth try: use regex to extract JSON object
    try:
        # Find the outermost JSON object
        match = re.search(r'\{[\s\S]*\}', cleaned)
        if match:
            extracted = match.group(0)
            data = json.loads(extracted)
            return True, data, ""
    except json.JSONDecodeError:
        pass
    
    # Fifth try: truncate at last valid closing bracket (for arrays)
    try:
        last_bracket = cleaned.rfind(']')
        if last_bracket > 0:
            truncated = cleaned[:last_bracket + 1]
            # Balance the brackets
            open_count = truncated.count('[')
            close_count = truncated.count(']')
            if open_count > close_count:
                truncated += ']' * (open_count - close_count)
            data = json.loads(truncated)
            return True, data, ""
    except json.JSONDecodeError:
        pass
    
    # Sixth try: truncate at last valid closing brace (for objects)
    try:
        last_brace = cleaned.rfind('}')
        if last_brace > 0:
            truncated = cleaned[:last_brace + 1]
            # Balance the braces
            open_count = truncated.count('{')
            close_count = truncated.count('}')
            if open_count > close_count:
                truncated += '}' * (open_count - close_count)
            data = json.loads(truncated)
            return True, data, ""
    except json.JSONDecodeError:
        pass
    
    # Seventh try: Use aggressive quiz repair function
    try:
        repaired = repair_quiz_json(cleaned)
        if repaired and len(repaired) > 0:
            print(f"[JSON REPAIR] Successfully extracted {len(repaired)} questions from malformed JSON")
            return True, repaired, ""
    except Exception as e:
        print(f"[JSON REPAIR] Failed: {e}")
        pass
    
    return False, None, f"JSON parse error: {first_error}"


def validate_topic_relevance(data: dict, topic: str) -> Tuple[bool, str]:
    """Validate that the generated content references the topic meaningfully."""
    content_str = json.dumps(data).lower()
    
    # Extract significant words from topic (ignore short words and special chars)
    topic_words = [
        word.strip() for word in topic.lower().replace('&', ' ').replace('-', ' ').split()
        if len(word.strip()) > 3
    ]
    
    if not topic_words:
        # If no significant words, just check the full topic
        topic_words = [topic.lower()]
    
    # Count how many topic words appear in the content
    words_found = 0
    word_counts = {}
    
    for word in topic_words:
        count = content_str.count(word)
        word_counts[word] = count
        if count >= 1:
            words_found += 1
    
    # Success if at least half of the topic words are found
    min_words_required = max(1, len(topic_words) // 2)
    
    if words_found < min_words_required:
        return False, f"Content doesn't reference topic '{topic}' enough. Words found: {word_counts}"
    
    # Also check that total mentions are reasonable (at least 5 total across all words)
    total_mentions = sum(word_counts.values())
    if total_mentions < 3:
        return False, f"Content has too few topic references (found {total_mentions} total mentions)"
    
    return True, ""


def validate_lesson_structure(lesson: dict) -> Tuple[bool, str]:
    """Validate that lesson content has proper structured format."""
    content = lesson.get("content", {})
    
    # Content should be a dict with structured fields
    if isinstance(content, str):
        return False, "Lesson content must be a structured object, not a string"
    
    if not isinstance(content, dict):
        return False, f"Lesson content must be an object, got {type(content).__name__}"
    
    # Critical required fields (must be present)
    critical_fields = [
        "introduction",
        "core_concepts",
        "guided_walkthrough",
        "practical_examples",
    ]
    
    # Optional fields that have fallbacks in course_generator.py
    # These include: lesson_overview, common_pitfalls, mental_model, summary, further_thinking
    
    for field in critical_fields:
        if field not in content:
            return False, f"Lesson content missing required field: {field}"
    
    # Validate content quality
    core_concepts = content.get("core_concepts", [])
    if not isinstance(core_concepts, list) or len(core_concepts) < 2:
        return False, "core_concepts must have at least 2 sections"
    
    walkthrough = content.get("guided_walkthrough", [])
    if not isinstance(walkthrough, list) or len(walkthrough) < 3:
        return False, "guided_walkthrough must have at least 3 steps"
    
    examples = content.get("practical_examples", [])
    if not isinstance(examples, list) or len(examples) < 2:
        return False, "practical_examples must have at least 2 examples"
    
    # Check introduction length (should be substantial)
    intro = content.get("introduction", "")
    if len(intro) < 100:
        return False, "introduction is too short (must be at least 100 characters)"
    
    # Check mental model length only if provided
    mental = content.get("mental_model", "")
    if mental and len(mental) < 50:
        return False, "mental_model is too short (must be at least 50 characters)"
    
    return True, ""


def validate_course_schema(data: dict) -> Tuple[bool, str]:
    """Validate that course data matches expected schema."""
    required_fields = ["title", "overview", "modules"]
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    if not isinstance(data["modules"], list) or len(data["modules"]) == 0:
        return False, "Modules must be a non-empty list"
    
    for i, module in enumerate(data["modules"]):
        if "module_title" not in module:
            return False, f"Module {i} missing module_title"
        if "lessons" not in module or not isinstance(module["lessons"], list):
            return False, f"Module {i} missing lessons array"
        
        for j, lesson in enumerate(module.get("lessons", [])):
            lesson_required = ["lesson_title", "bloom_level", "learning_outcomes", "content"]
            for field in lesson_required:
                if field not in lesson:
                    return False, f"Module {i}, Lesson {j} missing {field}"
            
            valid_levels = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
            if lesson.get("bloom_level") not in valid_levels:
                return False, f"Invalid bloom_level: {lesson.get('bloom_level')}"
            
            # Validate lesson structure
            struct_valid, struct_error = validate_lesson_structure(lesson)
            if not struct_valid:
                return False, f"Module {i}, Lesson {j}: {struct_error}"
    
    return True, ""


def validate_quiz_schema(data: list) -> Tuple[bool, str]:
    """Validate that quiz data matches expected schema."""
    if not isinstance(data, list):
        # Try to extract array if wrapped in object
        if isinstance(data, dict):
            if "questions" in data:
                data = data["questions"]
            else:
                # Try to find any list in the dict
                for key, value in data.items():
                    if isinstance(value, list) and len(value) > 0:
                        data = value
                        break
        if not isinstance(data, list):
            return False, "Quiz must be a list of questions"
    
    if len(data) == 0:
        return False, "Quiz must have at least one question"
    
    for i, q in enumerate(data):
        if not isinstance(q, dict):
            return False, f"Question {i} must be an object"
            
        required = ["question", "options", "correct_answer"]
        for field in required:
            if field not in q:
                return False, f"Question {i} missing {field}"
        
        if not isinstance(q["options"], list) or len(q["options"]) < 2:
            return False, f"Question {i} must have at least 2 options"
        
        if q["correct_answer"] not in q["options"]:
            # Try to find a close match
            correct = q["correct_answer"]
            matched = False
            for opt in q["options"]:
                if correct.lower().strip() == opt.lower().strip():
                    q["correct_answer"] = opt
                    matched = True
                    break
            if not matched:
                return False, f"Question {i} correct_answer must be in options"
    
    return True, ""


# ============== Prompt Builders ==============

def get_difficulty_instructions(difficulty: str) -> dict:
    """Get specific instructions for different difficulty levels."""
    difficulty_map = {
        "Beginner": {
            "tone": "patient and encouraging, assuming minimal prior knowledge",
            "explanations": "Start from first principles. Use simple language and avoid jargon. When technical terms are needed, define them clearly. Use plenty of analogies and real-world comparisons.",
            "examples": "Provide step-by-step walkthroughs with detailed explanations of each step. Include 3-4 practical examples per lesson with extensive commentary.",
            "depth": "Focus on fundamental concepts and basic applications. Build confidence before introducing complexity.",
            "complexity": "Keep examples simple and focused on one concept at a time. Avoid edge cases and advanced patterns.",
        },
        "Intermediate": {
            "tone": "conversational but professional, assuming basic familiarity with programming",
            "explanations": "Balance theory with practice. Use technical terminology appropriately with brief explanations. Connect new concepts to what learners likely already know.",
            "examples": "Show practical applications with moderate complexity. Include 2-3 examples that demonstrate real-world usage patterns.",
            "depth": "Cover both fundamentals and practical applications. Introduce some best practices and common patterns.",
            "complexity": "Use realistic examples that combine multiple concepts. Mention important edge cases.",
        },
        "Advanced": {
            "tone": "technical and precise, assuming strong programming background",
            "explanations": "Focus on deep understanding, edge cases, and architectural considerations. Discuss trade-offs and performance implications.",
            "examples": "Show advanced patterns, optimization techniques, and complex scenarios. Include 2-3 sophisticated examples.",
            "depth": "Explore advanced concepts, internal workings, and expert-level techniques. Discuss when and why to use different approaches.",
            "complexity": "Present complex, production-ready examples. Cover edge cases, error handling, and performance considerations.",
        }
    }
    return difficulty_map.get(difficulty, difficulty_map["Intermediate"])

def build_course_generation_prompt(topic: str, duration_hours: int, difficulty: str = "Intermediate") -> str:
    """
    Build a prompt for generating COMPREHENSIVE, PROFESSIONAL course content.
    Each lesson is a full learning document like a textbook chapter.
    """
    num_modules = max(2, min(6, duration_hours // 2))
    lessons_per_module = max(2, min(3, duration_hours // num_modules))
    # Get difficulty-specific instructions
    diff_instructions = get_difficulty_instructions(difficulty)


    # Build Bloom level descriptions for the prompt
    bloom_instructions = "\n".join([
        f"- {level}: {info['teaching_approach']}"
        for level, info in BLOOM_LEVELS.items()
    ])
    
    prompt = f"""Create a COMPREHENSIVE professional course about "{topic}".

=== CRITICAL INSTRUCTION ===
You are creating REAL COURSE CONTENT, not summaries.
Each lesson must be a COMPLETE LEARNING DOCUMENT that takes 20-40 minutes to read.
Write like you're creating content for The Odin Project or MDN tutorials.
=== DIFFICULTY LEVEL: {difficulty.upper()} ===

TONE: {diff_instructions['tone']}

EXPLANATIONS: {diff_instructions['explanations']}

EXAMPLES: {diff_instructions['examples']}

DEPTH: {diff_instructions['depth']}

COMPLEXITY: {diff_instructions['complexity']}


=== COURSE STRUCTURE ===
- Topic: {topic}
- Duration: {duration_hours} hours total
- Difficulty: {difficulty}
- Modules: {num_modules} modules
- Lessons per module: {lessons_per_module}

=== BLOOM'S TAXONOMY PROGRESSION ===
Structure the course to progress through cognitive levels:
{bloom_instructions}

=== MANDATORY LESSON CONTENT STRUCTURE ===

Each lesson's "content" field MUST be a JSON object with ALL these sections:

{{
  "introduction": "1-2 substantial paragraphs setting context. Assume learner has completed prior lessons. Use friendly instructor tone. Explain why this topic matters.",
  
  "lesson_overview": [
    "First major topic we'll cover",
    "Second major topic we'll cover", 
    "Third major topic we'll cover",
    "What you'll be able to do after this lesson"
  ],
  
  "core_concepts": [
    {{
      "title": "First Core Concept Title",
      "explanation": "2-3 detailed paragraphs explaining this concept thoroughly. Include the what, why, and how. Use analogies where helpful. This should be substantial teaching content, not a summary.",
      "code_example": "// Optional code example\\nfunction example() {{\\n  return 'relevant code';\\n}}"
    }},
    {{
      "title": "Second Core Concept Title",
      "explanation": "Another 2-3 paragraphs of detailed explanation. Build on the previous concept. Connect ideas together.",
      "code_example": null
    }}
  ],
  
  "guided_walkthrough": [
    "Step 1: Start with the fundamental building block. Explain what we're doing and why.",
    "Step 2: Build on step 1 by adding the next layer. Explain the connection.",
    "Step 3: Introduce a variation or edge case. Explain how to handle it.",
    "Step 4: Show how everything comes together. Provide the complete picture.",
    "Step 5: Explain what to watch out for and how to verify correctness."
  ],
  
  "practical_examples": [
    {{
      "description": "Real-world scenario where this applies",
      "code": "// Complete working code example\\nconst example = () => {{\\n  // implementation\\n}};",
      "explanation": "Detailed explanation of how this code works and why each part matters."
    }},
    {{
      "description": "Another practical application",
      "code": "// Another code example or null if not applicable",
      "explanation": "Walk through this example step by step."
    }}
  ],
  
  "common_pitfalls": [
    "Mistake 1: Description of what goes wrong and WHY it happens",
    "Mistake 2: Another common error with explanation of the underlying cause",
    "Mistake 3: A subtle issue that even experienced developers encounter"
  ],
  
  "mental_model": "A clear analogy or visualization that helps learners think correctly about this concept. For example, think of X like Y because... This should be memorable and help cement understanding.",
  
  "summary": "A comprehensive recap of the key points covered in this lesson. Reinforce the main takeaways. Connect back to the learning objectives. This should be 2-3 sentences.",
  
  "further_thinking": [
    "Reflective question 1 aligned with the Bloom level",
    "Application prompt 2 that encourages deeper thinking",
    "Challenge question 3 that extends the learning"
  ]
}}

=== CONTENT REQUIREMENTS ===

FOR THE TOPIC "{topic}":
1. Use real terminology and concepts from {topic}
2. Include practical, working code examples where applicable
3. Reference real tools, libraries, or practices used in {topic}
4. Make examples specific to {topic}, NOT generic programming examples
5. Ensure content builds progressively from module to module

=== QUIZ REQUIREMENTS ===

Each lesson needs 3 quiz questions:
- Mix of difficulty levels (easy, medium, hard)
- Aligned with the Bloom level of the lesson
- Include explanation for the correct answer

=== JSON OUTPUT SCHEMA ===

Return ONLY this JSON (no other text, no markdown code blocks):

{{
  "title": "Professional course title about {topic}",
  "overview": "2-3 sentences describing what learners will master in this course",
  "modules": [
    {{
      "module_title": "Module 1: Foundation of {topic}",
      "module_description": "What this module covers and why it matters",
      "lessons": [
        {{
          "lesson_title": "Specific lesson title about {topic}",
          "bloom_level": "Remember",
          "learning_outcomes": [
            "Specific, measurable outcome 1",
            "Specific, measurable outcome 2"
          ],
          "content": {{THE FULL STRUCTURED CONTENT OBJECT AS SHOWN ABOVE}},
          "estimated_duration_minutes": 30,
          "quiz": [
            {{
              "question": "Specific question about {topic}",
              "options": ["Correct answer", "Plausible wrong 1", "Plausible wrong 2", "Plausible wrong 3"],
              "correct_answer": "Correct answer",
              "difficulty": "easy",
              "explanation": "Why this is correct and what to understand"
            }}
          ]
        }}
      ]
    }}
  ]
}}

REMEMBER: 
- Each lesson content must be COMPREHENSIVE and STRUCTURED
- Do NOT write short summaries - write REAL educational content
- The content object must have ALL required fields
- This should feel like reading a professional course, not a blog post"""

    return prompt


def build_quiz_generation_prompt(
    lesson_content: str,
    bloom_level: str,
    difficulty: str,
    num_questions: int = 3,
    additional_instructions: str = ""
) -> str:
    """Build a prompt for quiz generation based on lesson content."""
    bloom_info = BLOOM_LEVELS.get(bloom_level, BLOOM_LEVELS["Remember"])
    
    # Add adaptation instructions if provided
    adaptation_section = ""
    if additional_instructions:
        adaptation_section = f"""
ADAPTATION INSTRUCTIONS (IMPORTANT - follow these to improve learning experience):
{additional_instructions}
"""
    
    prompt = f"""Generate exactly {num_questions} quiz questions based on this lesson content.

LESSON CONTENT:
{lesson_content}

REQUIREMENTS:
1. Questions must test {bloom_level} level: {bloom_info['description']}
2. Difficulty: {difficulty}
3. Question types to use: {', '.join(bloom_info['question_types'])}
4. Each question: exactly 4 options, 1 correct answer
5. Include explanation for correct answer
{adaptation_section}

CRITICAL: Output ONLY a valid JSON array. No markdown, no code blocks, no explanatory text.
Start with [ and end with ]

EXACT FORMAT - copy this structure precisely:
[
  {{"question": "What is X?", "options": ["A", "B", "C", "D"], "correct_answer": "A", "difficulty": "{difficulty}", "explanation": "A is correct because..."}}
]

Generate {num_questions} questions in this exact JSON array format. The correct_answer MUST exactly match one of the options."""
    
    return prompt


def build_regeneration_prompt(
    original_content: dict,
    feedback_type: str,
    additional_context: Optional[str] = None
) -> str:
    """Build a prompt for content regeneration based on user feedback."""
    feedback_instructions = {
        "too_easy": "Make content more challenging with advanced concepts and deeper analysis.",
        "too_hard": "Simplify with clearer language, basic examples, and step-by-step breakdowns.",
        "unclear": "Improve clarity with better structure, more examples, and simpler explanations.",
        "more_examples": "Add practical examples, code samples, and real-world applications.",
        "different_approach": "Use a completely different teaching approach or perspective."
    }
    
    instruction = feedback_instructions.get(feedback_type, "Improve this content.")
    bloom_level = original_content.get("bloom_level", "Remember")
    
    prompt = f"""Regenerate this educational content based on feedback.

ORIGINAL:
{json.dumps(original_content, indent=2)}

FEEDBACK: {feedback_type}
INSTRUCTION: {instruction}
{f"ADDITIONAL CONTEXT: {additional_context}" if additional_context else ""}

REQUIREMENTS:
1. Keep Bloom level: {bloom_level}
2. Keep the structured format with ## headers
3. Apply the feedback to improve content
4. Return complete improved content in same JSON structure

Return ONLY the JSON object."""
    
    return prompt


# ============== LLM Calling Functions ==============

async def call_llm(
    prompt: str,
    use_strict: bool = False
) -> Tuple[bool, Optional[str], str]:
    """Call the Perplexity LLM with the given prompt."""
    if USE_MOCK:
        return False, None, "Mock mode is enabled - disable USE_MOCK_LLM in .env"
    
    if not OPENAI_API_KEY:
        return False, None, "API key not configured - set OPENAI_API_KEY in .env"
    
    system_prompt = STRICT_SYSTEM_PROMPT if use_strict else SYSTEM_PROMPT
    
    try:
        client = get_openai_client()
        
        print(f"[LLM] Calling {MODEL_NAME} at {OPENAI_BASE_URL}")
        
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        
        content = response.choices[0].message.content
        print(f"[LLM] Response received, length: {len(content)} chars")
        
        return True, content, ""
        
    except RateLimitError as e:
        return False, None, f"Rate limit exceeded: {str(e)}"
    except APIConnectionError as e:
        return False, None, f"Connection error: {str(e)}"
    except APIError as e:
        return False, None, f"API error: {str(e)}"
    except Exception as e:
        return False, None, f"Unexpected error: {str(e)}"


async def call_llm_with_retry(
    prompt: str,
    validator: callable = None,
    topic: str = None
) -> Tuple[bool, Optional[dict], str]:
    """Call LLM with retry logic and validation. NO FALLBACK."""
    errors = []
    
    for attempt in range(MAX_RETRIES):
        use_strict = attempt > 0
        
        print(f"[LLM] Attempt {attempt + 1}/{MAX_RETRIES}")
        success, response, error = await call_llm(prompt, use_strict)
        
        if not success:
            errors.append(f"Attempt {attempt + 1}: {error}")
            if attempt < MAX_RETRIES - 1:
                continue
            return False, None, f"LLM call failed: {'; '.join(errors)}"
        
        # Log first 500 chars of raw response for debugging
        print(f"[LLM] Raw response preview: {response[:500] if response else 'None'}...")
        
        # Validate JSON
        is_valid, data, parse_error = validate_json(response)
        
        if not is_valid:
            errors.append(f"Attempt {attempt + 1}: {parse_error}")
            if attempt < MAX_RETRIES - 1:
                print(f"[LLM] JSON validation failed, retrying...")
                continue
            return False, None, f"JSON validation failed: {'; '.join(errors)}"
        
        # Run schema validator if provided
        if validator:
            schema_valid, schema_error = validator(data)
            if not schema_valid:
                errors.append(f"Attempt {attempt + 1}: Schema - {schema_error}")
                if attempt < MAX_RETRIES - 1:
                    print(f"[LLM] Schema validation failed, retrying...")
                    continue
                return False, None, f"Schema validation failed: {schema_error}"
        
        # Validate topic relevance if topic provided
        if topic:
            topic_valid, topic_error = validate_topic_relevance(data, topic)
            if not topic_valid:
                errors.append(f"Attempt {attempt + 1}: {topic_error}")
                if attempt < MAX_RETRIES - 1:
                    print(f"[LLM] Topic relevance check failed, retrying...")
                    continue
                return False, None, f"Content validation failed: {topic_error}"
        
        content_hash = compute_content_hash(data)
        print(f"[LLM] Success! Content hash: {content_hash}")
        
        return True, data, ""
    
    return False, None, f"All {MAX_RETRIES} attempts failed: {'; '.join(errors)}"


# ============== High-Level API Functions ==============

async def generate_course_content(topic: str, duration_hours: int, difficulty: str = "Intermediate") -> Tuple[bool, Optional[dict], str]:
    """Generate STRUCTURED course content using LLM. NO FALLBACK."""
    print(f"\n{'='*60}")
    print(f"[COURSE GENERATION] Topic: '{topic}', Duration: {duration_hours}h, Difficulty: {difficulty}")
    print(f"{'='*60}")
    
    prompt = build_course_generation_prompt(topic, duration_hours, difficulty)
    
    success, data, error = await call_llm_with_retry(
        prompt, 
        validate_course_schema,
        topic=topic
    )
    
    if success:
        content_hash = compute_content_hash(data)
        print(f"[COURSE GENERATION] Complete! Hash: {content_hash}")
        return True, data, "Course generated successfully"
    
    print(f"[COURSE GENERATION] FAILED: {error}")
    return False, None, f"Course generation failed: {error}"


async def generate_quiz_content(
    lesson_content: str,
    bloom_level: str,
    difficulty: str,
    num_questions: int = 3,
    additional_instructions: str = ""
) -> Tuple[bool, Optional[list], str]:
    """Generate quiz questions using LLM. NO FALLBACK."""
    print(f"\n[QUIZ GENERATION] Bloom: {bloom_level}, Difficulty: {difficulty}")
    if additional_instructions:
        print(f"[QUIZ GENERATION] Adaptation: {additional_instructions[:50]}...")
    
    prompt = build_quiz_generation_prompt(lesson_content, bloom_level, difficulty, num_questions, additional_instructions)
    
    success, data, error = await call_llm_with_retry(prompt, validate_quiz_schema)
    
    if success:
        print(f"[QUIZ GENERATION] Complete! Generated {len(data)} questions")
        return True, data, "Quiz generated successfully"
    
    print(f"[QUIZ GENERATION] FAILED: {error}")
    return False, None, f"Quiz generation failed: {error}"


async def regenerate_lesson_content(
    original_content: dict,
    feedback_type: str,
    additional_comments: Optional[str] = None
) -> Tuple[bool, Optional[dict], str]:
    """Regenerate lesson content based on feedback. NO FALLBACK."""
    print(f"\n[REGENERATION] Feedback: {feedback_type}")
    
    prompt = build_regeneration_prompt(original_content, feedback_type, additional_comments)
    
    success, data, error = await call_llm_with_retry(prompt)
    
    if success:
        print(f"[REGENERATION] Complete!")
        return True, data, "Content regenerated successfully"
    
    print(f"[REGENERATION] FAILED: {error}")
    return False, None, f"Regeneration failed: {error}"
