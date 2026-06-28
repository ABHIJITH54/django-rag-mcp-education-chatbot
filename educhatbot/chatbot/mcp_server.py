import os

import django
from mcp.server.fastmcp import FastMCP


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "educhatbot.settings")
django.setup()

from chatbot.tools import (
    build_study_plan,
    build_study_plan_until_exam,
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


mcp = FastMCP("edu-chatbot-live-db")


@mcp.tool()
def student_progress(student_name: str, course_id: int | None = None) -> dict:
    """Read student progress from the live Django SQLite database."""
    return get_student_progress(student_name, course_id)


@mcp.tool()
def student_profile(student_name: str) -> dict:
    """Read student profile details such as email, phone, city, and join date."""
    return get_student_profile(student_name)


@mcp.tool()
def enrolled_courses(student_name: str) -> list[dict]:
    """List courses purchased/enrolled by a student."""
    return get_enrolled_courses(student_name)


@mcp.tool()
def course_syllabus(course_id: int) -> dict:
    """List all syllabus topics for a course."""
    return get_course_syllabus(course_id)


@mcp.tool()
def pending_topics(student_name: str, course_id: int) -> dict:
    """Show completed, pending, and weak topics for a student."""
    return get_pending_topics(student_name, course_id)


@mcp.tool()
def next_exam(student_name: str, course_id: int | None = None) -> dict:
    """Find the next upcoming exam and remaining days."""
    return get_next_exam_for_student(student_name, course_id)


@mcp.tool()
def mock_test_results(student_name: str, course_id: int | None = None) -> list[dict]:
    """Read mock test score, rank, and weak-topic history."""
    return get_mock_test_results(student_name, course_id)


@mcp.tool()
def attendance_summary(student_name: str, course_id: int | None = None) -> dict:
    """Summarize attendance and recent attended/missed classes."""
    return get_attendance_summary(student_name, course_id)


@mcp.tool()
def upcoming_live_classes(student_name: str | None = None, course_id: int | None = None) -> list[dict]:
    """List upcoming live classes and meeting links."""
    return get_upcoming_live_classes(student_name, course_id)


@mcp.tool()
def payment_status(student_name: str, course_id: int | None = None) -> list[dict]:
    """Read payment status and transaction details."""
    return get_payment_status(student_name, course_id)


@mcp.tool()
def material_download_links(title: str, course_id: int | None = None) -> list[dict]:
    """Find study material PDF/download links from the live database."""
    return search_materials(title, course_id)


@mcp.tool()
def course_materials(course_id: int) -> list[dict]:
    """List all study material download links for a course."""
    return get_course_materials(course_id)


@mcp.tool()
def study_plan(student_name: str, course_id: int, days: int = 20) -> dict:
    """Create a day-wise study plan using live DB course topics and progress."""
    return build_study_plan(student_name, course_id, days)


@mcp.tool()
def study_plan_until_exam(student_name: str, course_id: int) -> dict:
    """Create a study plan using remaining days before the next exam."""
    return build_study_plan_until_exam(student_name, course_id)


@mcp.tool()
def student_dashboard(student_name: str, course_id: int | None = None) -> dict:
    """Return a full student dashboard from the live DB."""
    return get_student_dashboard(student_name, course_id)


if __name__ == "__main__":
    mcp.run()
