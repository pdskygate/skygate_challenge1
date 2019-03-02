from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from exams_app.exams.serializers import ExamSerializer


class ExamManagementView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BasicAuthentication,)
    serializer_class = ExamSerializer

    def get_queryset(self):
        pass

    def list(self, request, **kwargs):
        pass

    def create(self, request, *args, **kwargs):
        pass

    def update(self, request, *args, **kwargs):
        pass