from .llm import ask_llm
from .rag import search_documents
from .tools import (
    build_study_plan,
    build_study_plan_until_exam,
    generate_study_plan_pdf,
    get_attendance_summary,
    get_course_materials,
    get_course_syllabus,
    get_enrolled_courses,
    get_mock_test_results,
    get_next_exam_for_student,
    get_payment_status,
    get_pending_topics,
    get_student_dashboard,
    get_student_profile,
    get_student_progress,
    get_upcoming_live_classes,
    search_materials,
)


def answer_chat(student_name, question, course_id=None):
    question_lower = question.lower()
    rag_matches = search_documents(question, course_id=course_id, limit=5)
    progress = get_student_progress(student_name, course_id=course_id)

    tool_results = run_relevant_tools(student_name, question_lower, course_id)

    document_context = "\n\n".join(
        [
            f"Source: {match['metadata'].get('material_title')} page {match['metadata'].get('page')}\n{match['text']}"
            for match in rag_matches
        ]
    )

    prompt = f"""
You are a helpful education chatbot for an e-learning platform.

Rules:
- Use the document context for syllabus/notes facts.
- Use live DB progress for personalization.
- If a download link is available, mention it clearly.
- If creating a study plan, make it practical and day-wise.
- If exam data is available, use remaining days before exam.
- If information is missing, say what is missing.

Student name:
{student_name}

Live DB progress:
{progress}

Tool results:
{tool_results}

Document context from RAG:
{document_context}

Student question:
{question}
"""

    return {
        "answer": ask_llm(prompt),
        "rag_sources": [match["metadata"] for match in rag_matches],
        "live_db_progress": progress,
        "tool_results": tool_results,
    }


def run_relevant_tools(student_name, question_lower, course_id=None):
    results = []
    numeric_course_id = int(course_id) if course_id else None

    if _has_any(question_lower, ["profile", "my details", "my account", "phone", "email"]):
        results.append({"tool": "get_student_profile", "result": get_student_profile(student_name)})

    if _has_any(question_lower, ["enrolled", "my courses", "purchased courses", "joined courses"]):
        results.append({"tool": "get_enrolled_courses", "result": get_enrolled_courses(student_name)})

    if _has_any(question_lower, ["progress", "completed", "weak", "pending topic", "pending syllabus"]):
        results.append({"tool": "get_student_progress", "result": get_student_progress(student_name, course_id)})
        if numeric_course_id:
            results.append({"tool": "get_pending_topics", "result": get_pending_topics(student_name, numeric_course_id)})

    if _has_any(question_lower, ["syllabus", "topics"]):
        if numeric_course_id:
            results.append({"tool": "get_course_syllabus", "result": get_course_syllabus(numeric_course_id)})

    if _has_any(question_lower, ["exam", "exam date", "next month"]):
        results.append({"tool": "get_next_exam_for_student", "result": get_next_exam_for_student(student_name, course_id)})

    if _has_any(question_lower, ["mock", "mark", "score", "rank", "result"]):
        results.append({"tool": "get_mock_test_results", "result": get_mock_test_results(student_name, course_id)})

    if _has_any(question_lower, ["attendance", "attended", "missed class"]):
        results.append({"tool": "get_attendance_summary", "result": get_attendance_summary(student_name, course_id)})

    if _has_any(question_lower, ["live class", "next class", "meeting", "class link"]):
        results.append({"tool": "get_upcoming_live_classes", "result": get_upcoming_live_classes(student_name, course_id)})

    if _has_any(question_lower, ["payment", "paid", "purchase", "transaction", "fee"]):
        results.append({"tool": "get_payment_status", "result": get_payment_status(student_name, course_id)})

    if _has_any(question_lower, ["download", "pdf", "notes", "material"]):
        results.append({"tool": "search_materials", "result": search_materials(question_lower, course_id=course_id)})
        if numeric_course_id:
            results.append({"tool": "get_course_materials", "result": get_course_materials(numeric_course_id)})

    if _has_any(question_lower, ["study plan", "timetable", "schedule to study", "complete the syllabus"]):
        if numeric_course_id:
            days = _extract_days(question_lower)
            if days:
                plan = build_study_plan(student_name, numeric_course_id, days)
            else:
                plan = build_study_plan_until_exam(student_name, numeric_course_id)
            results.append({"tool": "build_study_plan", "result": plan})

    if _has_any(question_lower, ["dashboard", "summary", "overall", "everything"]):
        results.append({"tool": "get_student_dashboard", "result": get_student_dashboard(student_name, course_id)})

    if not results:
        results.append({"tool": "get_student_progress", "result": get_student_progress(student_name, course_id)})

    return results


def _extract_days(text):
    words = text.replace("-", " ").split()
    for index, word in enumerate(words):
        if word.isdigit():
            number = int(word)
            if index + 1 < len(words) and words[index + 1] in {"day", "days"}:
                return number
    return None


def _has_any(text, keywords):
    return any(keyword in text for keyword in keywords)


def create_plan_pdf(student_name, course_id, days):
    plan = build_study_plan(student_name, int(course_id), int(days))
    pdf_url = generate_study_plan_pdf(plan)
    return {"plan": plan, "pdf_url": pdf_url}
