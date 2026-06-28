from django.db import models

# Create your models here.
from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.title


class Topic(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="topics")
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["course", "order", "title"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class StudentProfile(models.Model):
    student_name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=120, blank=True)
    joined_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.student_name


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("expired", "Expired"),
        ("completed", "Completed"),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    enrolled_at = models.DateField(null=True, blank=True)
    expires_at = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student.student_name} - {self.course.title}"


class StudyMaterial(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="materials")
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="materials/")
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class StudentProgress(models.Model):
    student_name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="progress")
    completed_topics = models.JSONField(default=list, blank=True)
    weak_topics = models.JSONField(default=list, blank=True)
    exam_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student_name", "course")

    def __str__(self):
        return f"{self.student_name} - {self.course.title}"


class ExamSchedule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="exams")
    title = models.CharField(max_length=255)
    exam_date = models.DateField()
    syllabus_topics = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["exam_date"]

    def __str__(self):
        return f"{self.title} - {self.exam_date}"


class MockTestResult(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="mock_tests")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="mock_tests")
    title = models.CharField(max_length=255)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    rank = models.PositiveIntegerField(null=True, blank=True)
    weak_topics = models.JSONField(default=list, blank=True)
    attempted_at = models.DateField()

    class Meta:
        ordering = ["-attempted_at"]

    def __str__(self):
        return f"{self.student.student_name} - {self.title}"


class AttendanceRecord(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="attendance")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="attendance")
    class_title = models.CharField(max_length=255)
    attended = models.BooleanField(default=False)
    class_date = models.DateField()

    class Meta:
        ordering = ["-class_date"]

    def __str__(self):
        return f"{self.student.student_name} - {self.class_title}"


class LiveClass(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="live_classes")
    title = models.CharField(max_length=255)
    starts_at = models.DateTimeField()
    meeting_url = models.URLField(blank=True)
    is_recorded = models.BooleanField(default=False)

    class Meta:
        ordering = ["starts_at"]

    def __str__(self):
        return self.title


class PaymentRecord(models.Model):
    STATUS_CHOICES = [
        ("paid", "Paid"),
        ("pending", "Pending"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="payments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    paid_at = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["-paid_at", "-id"]

    def __str__(self):
        return f"{self.student.student_name} - {self.course.title} - {self.status}"
