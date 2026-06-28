from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import answer_chat, create_plan_pdf
from .tools import search_materials


class ChatAPIView(APIView):
    def post(self, request):
        student_name = request.data.get("student_name", "").strip()
        question = request.data.get("question", "").strip()
        course_id = request.data.get("course_id")

        if not student_name or not question:
            return Response(
                {"error": "student_name and question are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = answer_chat(student_name, question, course_id=course_id)
        return Response(data)


class MaterialSearchAPIView(APIView):
    def get(self, request):
        title = request.GET.get("title", "")
        course_id = request.GET.get("course_id")
        return Response({"data": search_materials(title, course_id=course_id)})


class GenerateStudyPlanPDFAPIView(APIView):
    def post(self, request):
        student_name = request.data.get("student_name", "").strip()
        course_id = request.data.get("course_id")
        days = request.data.get("days", 20)

        if not student_name or not course_id:
            return Response(
                {"error": "student_name and course_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(create_plan_pdf(student_name, course_id, days))
