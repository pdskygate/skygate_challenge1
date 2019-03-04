"""exams_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from exams_app.exams.views import ExamManagementView, SolveExamView

router = routers.DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
    url('solve_exam/', SolveExamView.as_view({
        'post':'create',
        'put':'update'
    })),
    url('exam/(?P<exam_id>[0-9]+)', ExamManagementView.as_view({
        'get':'list',
        'delete':'destroy'
    })),
    url('exam', ExamManagementView.as_view({
        'get':'list',
        'post':'create',
        'put':'update'
    })),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
