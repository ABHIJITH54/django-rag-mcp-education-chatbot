from django.urls import path

from .views import ChatAPIView, GenerateStudyPlanPDFAPIView, MaterialSearchAPIView


urlpatterns = [
    path("chat/", ChatAPIView.as_view(), name="chat"),
    path("materials/search/", MaterialSearchAPIView.as_view(), name="material-search"),
    path("study-plan/pdf/", GenerateStudyPlanPDFAPIView.as_view(), name="study-plan-pdf"),
]
