from datetime import date, datetime, time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

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
    Topic,
)


class Command(BaseCommand):
    help = "Create demo education data."

    def handle(self, *args, **options):
        course, _ = Course.objects.get_or_create(
            title="PSC Foundation",
            defaults={
                "description": "Demo PSC course for RAG chatbot testing.",
                "price": 4999,
            },
        )

        topics = [
            "Indian Constitution",
            "Kerala Renaissance",
            "Modern Indian History",
            "Geography of India",
            "Basic Science",
            "Current Affairs",
            "Quantitative Aptitude",
            "English Grammar",
        ]

        for order, title in enumerate(topics, start=1):
            Topic.objects.get_or_create(course=course, title=title, defaults={"order": order})

        StudentProgress.objects.update_or_create(
            student_name="Abhi",
            course=course,
            defaults={
                "completed_topics": ["Indian Constitution", "English Grammar"],
                "weak_topics": ["Quantitative Aptitude", "Current Affairs"],
                "exam_date": date.today() + timedelta(days=30),
            },
        )

        student, _ = StudentProfile.objects.update_or_create(
            student_name="Abhi",
            defaults={
                "email": "abhi@example.com",
                "phone": "9999999999",
                "city": "Kochi",
                "joined_at": date.today() - timedelta(days=45),
            },
        )

        Enrollment.objects.update_or_create(
            student=student,
            course=course,
            defaults={
                "status": "active",
                "enrolled_at": date.today() - timedelta(days=30),
                "expires_at": date.today() + timedelta(days=180),
            },
        )

        ExamSchedule.objects.update_or_create(
            course=course,
            title="PSC Preliminary Exam",
            defaults={
                "exam_date": date.today() + timedelta(days=30),
                "syllabus_topics": topics,
            },
        )

        MockTestResult.objects.update_or_create(
            student=student,
            course=course,
            title="Mock Test 1",
            defaults={
                "score": 62,
                "total_marks": 100,
                "rank": 18,
                "weak_topics": ["Quantitative Aptitude", "Current Affairs"],
                "attempted_at": date.today() - timedelta(days=5),
            },
        )

        MockTestResult.objects.update_or_create(
            student=student,
            course=course,
            title="Mock Test 2",
            defaults={
                "score": 71,
                "total_marks": 100,
                "rank": 11,
                "weak_topics": ["Current Affairs"],
                "attempted_at": date.today() - timedelta(days=1),
            },
        )

        AttendanceRecord.objects.update_or_create(
            student=student,
            course=course,
            class_title="Indian Constitution Basics",
            class_date=date.today() - timedelta(days=2),
            defaults={"attended": True},
        )

        AttendanceRecord.objects.update_or_create(
            student=student,
            course=course,
            class_title="Quantitative Aptitude Practice",
            class_date=date.today() - timedelta(days=1),
            defaults={"attended": False},
        )

        starts_at = timezone.make_aware(
            datetime.combine(date.today() + timedelta(days=1), time(hour=19, minute=30))
        )
        LiveClass.objects.update_or_create(
            course=course,
            title="Current Affairs Revision",
            starts_at=starts_at,
            defaults={
                "meeting_url": "https://example.com/live/current-affairs",
                "is_recorded": True,
            },
        )

        PaymentRecord.objects.update_or_create(
            student=student,
            course=course,
            transaction_id="DEMO-TXN-001",
            defaults={
                "amount": 4999,
                "status": "paid",
                "paid_at": timezone.now() - timedelta(days=30),
            },
        )

        self.stdout.write(self.style.SUCCESS(f"Demo course id: {course.id}"))
