from datetime import date, timedelta

from django.conf import settings
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from learning.models import (
    AttendanceRecord,
    Course,
    Enrollment,
    ExamSchedule,
    LiveClass,
    MockTestResult,
    PaymentRecord,
    StudentProfile,
    StudentProgress,
    StudyMaterial,
)


def get_student_profile(student_name):
    student = StudentProfile.objects.filter(student_name__iexact=student_name).first()
    if not student:
        return {"found": False, "message": "No student profile found in live DB."}

    return {
        "found": True,
        "id": student.id,
        "student_name": student.student_name,
        "email": student.email,
        "phone": student.phone,
        "city": student.city,
        "joined_at": student.joined_at.isoformat() if student.joined_at else None,
    }


def get_student_progress(student_name, course_id=None):
    queryset = StudentProgress.objects.select_related("course").filter(
        student_name__iexact=student_name
    )
    if course_id:
        queryset = queryset.filter(course_id=course_id)

    progress = queryset.first()
    if not progress:
        return {
            "found": False,
            "message": "No student progress found in live DB.",
        }

    return {
        "found": True,
        "student_name": progress.student_name,
        "course_id": progress.course_id,
        "course": progress.course.title,
        "completed_topics": progress.completed_topics,
        "weak_topics": progress.weak_topics,
        "exam_date": progress.exam_date.isoformat() if progress.exam_date else None,
    }


def get_enrolled_courses(student_name):
    queryset = Enrollment.objects.select_related("student", "course").filter(
        student__student_name__iexact=student_name
    )

    return [
        {
            "course_id": item.course_id,
            "course": item.course.title,
            "status": item.status,
            "enrolled_at": item.enrolled_at.isoformat() if item.enrolled_at else None,
            "expires_at": item.expires_at.isoformat() if item.expires_at else None,
        }
        for item in queryset
    ]


def get_course_syllabus(course_id):
    course = Course.objects.prefetch_related("topics").filter(id=course_id).first()
    if not course:
        return {"found": False, "message": "Course not found."}

    return {
        "found": True,
        "course_id": course.id,
        "course": course.title,
        "topics": [{"id": topic.id, "title": topic.title, "order": topic.order} for topic in course.topics.all()],
    }


def get_pending_topics(student_name, course_id):
    syllabus = get_course_syllabus(course_id)
    progress = get_student_progress(student_name, course_id)

    if not syllabus.get("found"):
        return syllabus

    completed = set(progress.get("completed_topics", [])) if progress.get("found") else set()
    topics = [topic["title"] for topic in syllabus["topics"]]

    return {
        "student_name": student_name,
        "course_id": course_id,
        "course": syllabus["course"],
        "completed_topics": list(completed),
        "pending_topics": [topic for topic in topics if topic not in completed],
        "weak_topics": progress.get("weak_topics", []) if progress.get("found") else [],
    }


def get_exam_schedule(course_id=None):
    queryset = ExamSchedule.objects.select_related("course").all()
    if course_id:
        queryset = queryset.filter(course_id=course_id)

    today = date.today()
    return [
        {
            "id": exam.id,
            "course_id": exam.course_id,
            "course": exam.course.title,
            "title": exam.title,
            "exam_date": exam.exam_date.isoformat(),
            "days_remaining": max((exam.exam_date - today).days, 0),
            "syllabus_topics": exam.syllabus_topics,
        }
        for exam in queryset[:10]
    ]


def get_next_exam_for_student(student_name, course_id=None):
    enrollments = get_enrolled_courses(student_name)
    course_ids = [item["course_id"] for item in enrollments]
    if course_id:
        course_ids = [int(course_id)]

    exam = (
        ExamSchedule.objects.select_related("course")
        .filter(course_id__in=course_ids, exam_date__gte=date.today())
        .order_by("exam_date")
        .first()
    )

    if not exam:
        return {"found": False, "message": "No upcoming exam found."}

    return {
        "found": True,
        "course_id": exam.course_id,
        "course": exam.course.title,
        "title": exam.title,
        "exam_date": exam.exam_date.isoformat(),
        "days_remaining": max((exam.exam_date - date.today()).days, 0),
        "syllabus_topics": exam.syllabus_topics,
    }


def get_mock_test_results(student_name, course_id=None, limit=5):
    queryset = MockTestResult.objects.select_related("student", "course").filter(
        student__student_name__iexact=student_name
    )
    if course_id:
        queryset = queryset.filter(course_id=course_id)

    return [
        {
            "title": result.title,
            "course": result.course.title,
            "score": float(result.score),
            "total_marks": float(result.total_marks),
            "percentage": round(float(result.score) / float(result.total_marks) * 100, 2),
            "rank": result.rank,
            "weak_topics": result.weak_topics,
            "attempted_at": result.attempted_at.isoformat(),
        }
        for result in queryset[:limit]
    ]


def get_attendance_summary(student_name, course_id=None):
    queryset = AttendanceRecord.objects.select_related("student", "course").filter(
        student__student_name__iexact=student_name
    )
    if course_id:
        queryset = queryset.filter(course_id=course_id)

    total = queryset.count()
    attended = queryset.filter(attended=True).count()
    percentage = round((attended / total) * 100, 2) if total else 0

    return {
        "student_name": student_name,
        "course_id": course_id,
        "total_classes": total,
        "attended_classes": attended,
        "missed_classes": total - attended,
        "attendance_percentage": percentage,
        "recent_classes": [
            {
                "course": item.course.title,
                "class_title": item.class_title,
                "class_date": item.class_date.isoformat(),
                "attended": item.attended,
            }
            for item in queryset[:10]
        ],
    }


def get_upcoming_live_classes(student_name=None, course_id=None, limit=5):
    queryset = LiveClass.objects.select_related("course").filter(starts_at__gte=timezone.now())

    if course_id:
        queryset = queryset.filter(course_id=course_id)
    elif student_name:
        course_ids = [item["course_id"] for item in get_enrolled_courses(student_name)]
        queryset = queryset.filter(course_id__in=course_ids)

    return [
        {
            "title": live_class.title,
            "course": live_class.course.title,
            "starts_at": live_class.starts_at.isoformat(),
            "meeting_url": live_class.meeting_url,
            "is_recorded": live_class.is_recorded,
        }
        for live_class in queryset[:limit]
    ]


def get_payment_status(student_name, course_id=None):
    queryset = PaymentRecord.objects.select_related("student", "course").filter(
        student__student_name__iexact=student_name
    )
    if course_id:
        queryset = queryset.filter(course_id=course_id)

    return [
        {
            "course": payment.course.title,
            "amount": float(payment.amount),
            "status": payment.status,
            "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
            "transaction_id": payment.transaction_id,
        }
        for payment in queryset[:10]
    ]


def search_materials(title, course_id=None):
    queryset = StudyMaterial.objects.select_related("course").filter(
        title__icontains=title
    )
    if course_id:
        queryset = queryset.filter(course_id=course_id)

    return [
        {
            "id": material.id,
            "title": material.title,
            "course": material.course.title,
            "download_url": material.file.url,
            "is_public": material.is_public,
        }
        for material in queryset[:10]
    ]


def get_course_materials(course_id):
    queryset = StudyMaterial.objects.select_related("course").filter(course_id=course_id)
    return [
        {
            "id": material.id,
            "title": material.title,
            "course": material.course.title,
            "download_url": material.file.url,
            "is_public": material.is_public,
            "created_at": material.created_at.isoformat(),
        }
        for material in queryset
    ]


def get_student_dashboard(student_name, course_id=None):
    return {
        "profile": get_student_profile(student_name),
        "enrolled_courses": get_enrolled_courses(student_name),
        "progress": get_student_progress(student_name, course_id),
        "pending_topics": get_pending_topics(student_name, course_id) if course_id else None,
        "next_exam": get_next_exam_for_student(student_name, course_id),
        "mock_tests": get_mock_test_results(student_name, course_id),
        "attendance": get_attendance_summary(student_name, course_id),
        "live_classes": get_upcoming_live_classes(student_name, course_id),
        "payments": get_payment_status(student_name, course_id),
    }


def build_study_plan(student_name, course_id, days):
    course = Course.objects.prefetch_related("topics").get(id=course_id)
    progress = get_student_progress(student_name, course_id)
    completed = set(progress.get("completed_topics", [])) if progress.get("found") else set()
    weak_topics = set(progress.get("weak_topics", [])) if progress.get("found") else set()

    pending_topics = [
        topic.title
        for topic in course.topics.all()
        if topic.title not in completed
    ]

    if not pending_topics:
        pending_topics = [topic.title for topic in course.topics.all()]

    plan = []
    today = date.today()
    for index in range(days):
        topic = pending_topics[index % len(pending_topics)] if pending_topics else "Revision"
        task = f"Study {topic}"
        if topic in weak_topics:
            task += " with extra revision and practice questions"
        plan.append(
            {
                "day": index + 1,
                "date": (today + timedelta(days=index)).isoformat(),
                "task": task,
            }
        )

    return {
        "student_name": student_name,
        "course": course.title,
        "days": days,
        "pending_topics": pending_topics,
        "weak_topics": list(weak_topics),
        "plan": plan,
    }


def build_study_plan_until_exam(student_name, course_id):
    next_exam = get_next_exam_for_student(student_name, course_id)
    days = next_exam.get("days_remaining", 20) if next_exam.get("found") else 20
    plan = build_study_plan(student_name, course_id, max(days, 1))
    plan["exam"] = next_exam
    return plan


def generate_study_plan_pdf(plan_data):
    settings.CHATBOT_GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    file_name = f"study_plan_{plan_data['student_name'].replace(' ', '_')}.pdf"
    file_path = settings.CHATBOT_GENERATED_DIR / file_name

    pdf = canvas.Canvas(str(file_path), pagesize=A4)
    width, height = A4
    y = height - 50

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, f"{plan_data['course']} Study Plan")
    y -= 30

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, f"Student: {plan_data['student_name']}")
    y -= 25

    for item in plan_data["plan"]:
        if y < 70:
            pdf.showPage()
            pdf.setFont("Helvetica", 11)
            y = height - 50

        line = f"Day {item['day']} ({item['date']}): {item['task']}"
        pdf.drawString(50, y, line[:105])
        y -= 20

    pdf.save()
    return f"{settings.MEDIA_URL}generated/{file_name}"
