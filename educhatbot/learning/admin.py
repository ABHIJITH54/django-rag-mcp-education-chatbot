from django.contrib import admin

from .models import (
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
    Topic,
)


admin.site.register(Course)
admin.site.register(Topic)
admin.site.register(StudentProfile)
admin.site.register(Enrollment)
admin.site.register(StudyMaterial)
admin.site.register(StudentProgress)
admin.site.register(ExamSchedule)
admin.site.register(MockTestResult)
admin.site.register(AttendanceRecord)
admin.site.register(LiveClass)
admin.site.register(PaymentRecord)
