# from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from exams_app.exams.models import User, Exam, Question


class ExamManagement(APITestCase):
    fixtures = ['answer_possibility', 'question', 'question_type']

    def setUp(self):
        self.user_name = 'testuser'
        self.user_password = 'testpass'
        self.user = User(username=self.user_name)
        self.user.set_password(self.user_password)
        self.user.save()

    def test_create_exam(self):
        # given
        url = reverse('exam-list')
        data = {
            "q": [1, 2, 3]
        }

        # when
        self.client.login(username=self.user_name, password=self.user_password)
        response = self.client.post(url, data=data, format='json')

        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_exam(self):
        # given
        exam, owner = self._prepare_exam()
        url = reverse('exam-detail', kwargs={
            'pk': exam.id
        })
        data = {
            'q':[1]
        }
        self.client.login(username=self.user_name, password=self.user_password)
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

        self.client.login(username='owner', password='owner')
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_exam(self):
        # given
        exam, owner = self._prepare_exam()
        url = reverse('exam-detail', kwargs={
            'pk': exam.id
        })
        self.client.login(username=self.user_name, password=self.user_password)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

        self.client.login(username='owner', password='owner')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def _prepare_exam(self):
        owner = User(username='owner')
        owner.set_password('owner')
        owner.save()

        exam = Exam()
        exam.owner = owner
        exam.save()
        exam.questions.set(Question.objects.all())
        exam.save()
        return exam, owner
