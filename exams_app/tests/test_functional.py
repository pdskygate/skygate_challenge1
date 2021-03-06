# from django.contrib.auth.models import User
from datetime import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from exams_app.exams.models import User, Exam, Question, SolvedExam, Answer


class BaseTest(APITestCase):
    fixtures = ['answer_possibility', 'question', 'question_type']

    def setUp(self):
        self.user_name = 'baseuser'
        self.user_password = 'testpass'
        self.user = User(username=self.user_name)
        self.user.set_password(self.user_password)
        self.user.save()


class TestExamManagement(BaseTest):

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
            'q': [1]
        }
        # when
        self.client.login(username=self.user_name, password=self.user_password)
        response = self.client.put(url, data=data, format='json')
        # then
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # when
        self.client.logout()

        self.client.login(username='owner', password='owner')
        response = self.client.put(url, data=data, format='json')
        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_exam(self):
        # given
        exam, owner = self._prepare_exam()
        url = reverse('exam-detail', kwargs={
            'pk': exam.id
        })
        self.client.login(username=self.user_name, password=self.user_password)
        # when
        response = self.client.delete(url, format='json')
        # then
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

        self.client.login(username='owner', password='owner')
        # when
        response = self.client.delete(url, format='json')
        # then
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


class TestQuestionUpdateView(BaseTest):
    fixtures = ['answer_possibility', 'question', 'question_type']

    def setUp(self):
        super(TestQuestionUpdateView, self).setUp()
        self.user.reviewer = True
        self.user.save()


    def test_user_permission(self):
        # given
        user_name = 'testuser'
        user_password = 'testpass'
        user = User(username=user_name)
        user.set_password(user_password)
        user.save()

        url = reverse('question_update-detail', kwargs={
            'pk': 1
        })
        data = {}

        # when
        self.client.login(username=user_name, password=user_password)
        response = self.client.put(url, data={}, format='json')
        # then
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # when
        self.client.logout()
        self.client.login(username=self.user_name, password=self.user_password)
        response = self.client.put(url, data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_text_answer(self):
        # given
        pk = 2
        url = reverse('question_update-detail', kwargs={
            'pk': pk
        })
        data = {"max_grade": 12, 'correct_answer': 'ala'}
        q = Question.objects.get(pk=pk)
        a = q.correct_answer
        g = q.max_grade

        # when
        self.client.login(username=self.user_name, password=self.user_password)
        response = self.client.put(url, data=data, format='json')
        q = Question.objects.get(pk=pk)
        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(a, q.correct_answer)
        self.assertNotEqual(g, q.max_grade)

    def test_update_possibility_answer(self):
        # given
        pk = 1
        url = reverse('question_update-detail', kwargs={
            'pk': pk
        })
        data = {"one_of_poss": True, 'correct_answer': 3}
        q = Question.objects.get(pk=pk)
        a = q.correct_possibility

        # when
        self.client.login(username=self.user_name, password=self.user_password)
        response = self.client.put(url, data=data, format='json')
        q = Question.objects.get(pk=pk)
        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(a, q.correct_possibility)


class TestExamSolve(BaseTest):
    fixtures = ['answer_possibility', 'question', 'question_type']

    def setUp(self):
        super(TestExamSolve, self).setUp()

        self.exam = Exam()
        self.exam.owner = self.user
        self.exam.save()
        self.exam.questions.set(Question.objects.all()[:1])
        self.exam.save()

    def test_solve(self):
        # given
        url = reverse('solve_exam-list')
        self.client.login(username=self.user_name, password=self.user_password)
        data = {
            "exam_id": self.exam.id,
            "answers": {"1": 2}
        }
        # when
        response = self.client.post(url, data=data, format='json')

        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Question.objects.get(pk=1).max_grade, SolvedExam.objects.get(exam__pk=self.exam.id,
                                                                                      user__username=self.user_name).possible_grade)

        # when secenod try to solve
        response = self.client.post(url, data=data, format='json')
        # then
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_grade(self):
        # given
        user_name = 'testuser1'
        user_password = 'testpass'
        user = User(username=user_name)
        user.set_password(user_password)
        user.save()

        data = {
            "exam_id": self.exam.id,
            "answers": {"1": 2}
        }

        url = reverse('solve_exam-detail', kwargs={
            'pk': self.exam.id
        })

        # when
        response = self.client.put(url, format='json')
        self._solve_exam((user))
        # then
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.logout()
        data = {'final_grade': 23}
        self.client.login(username=self.user_name, password=self.user_password)
        # when
        response = self.client.put(url, data=data, format='json')
        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def _solve_exam(self, user):
        solved = SolvedExam()
        solved.exam = self.exam
        solved.user = user
        solved.date = datetime.now()
        solved.save()
        q = self.exam.questions.first()
        a = Answer()
        a.solved_exam = solved
        a.question = q
        a.set_value(q.question_type, 1)
        a.save()
