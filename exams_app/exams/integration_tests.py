from django.test import TestCase

from exams_app.exams.models import Question, Exam, User, QuestionType
from exams_app.exams.repositories import BaseRepository, ExamRepository


class CRUDTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(CRUDTestCase, cls).setUpClass()
        QuestionType.objects.create(type='test')
        Question.objects.create(text='test question', question_type=QuestionType.objects.first())
        Question.objects.create(text='test2 question', question_type=QuestionType.objects.first())
        User.objects.create(username='test_user', password='test_pass')
        e = Exam()
        e.save()
        e.owner = User.objects.first()
        e.questions.set(Question.objects.all())
        e.save()

    def test_create(self):
        # given
        exam_repo = ExamRepository(Exam)

        #when
        exam = self._create_test_exam()

        # then
        self.assertIsNotNone(exam_repo.find_by_id(exam.id))

    def test_update(self):
        # given
        exam_repo = ExamRepository(Exam)
        e = exam_repo.find_by_id(1)
        q_count = e.questions.all().count()

        #when
        exam_repo.update_model(e.id, questions=Question.objects.first())

        #then
        self.assertNotEqual(q_count, len(Exam.objects.get(id=1).questions.all()))

    def test_delete(self):
        #given
        count = Exam.objects.count()

        #when
        ExamRepository(Exam).delete_model(Exam.objects.first().id)

        self.assertLess(Exam.objects.count(), count)
        pass

    def test_filter(self):
        # given
        q_repo = BaseRepository(Question)

        # when
        q_set = q_repo.filter(id=1)

        # then
        self.assertEqual(q_set.count(), 1)

    def _create_test_exam(self):
        exam_repo = ExamRepository(Exam)
        questions = Question.objects.first()
        user = BaseRepository(User).find_by_id(1)

        exam = exam_repo.crate_model(questions, user)
        return exam
