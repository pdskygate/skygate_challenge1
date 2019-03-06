import abc
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from collections import abc as col_abc

from rest_framework.exceptions import PermissionDenied

from exams_app.exams.exceptions import InvalidParamError, SolvingError
from exams_app.exams.models import Exam, QuestionTypeEnum


class AbstractReposository(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def crate_model(self, **kwargs):
        pass

    @abc.abstractmethod
    def update_model(self, model_id, **kwargs):
        pass

    @abc.abstractmethod
    def delete_model(self, model_id):
        pass

    @abc.abstractmethod
    def find_by_id(self, model_id):
        pass

    @abc.abstractmethod
    def filter(self, **kwargs):
        pass


class BaseRepository(AbstractReposository):

    def __init__(self, model_class):
        self._model_class = model_class
        self._qs = None

    def crate_model(self, **kwargs):
        raise NotImplementedError('Cannot create, use specified repository')

    def update_model(self, model, **kwargs):
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)
        model.save()
        return model

    def delete_model(self, model_id):
        self._model_class.objects.get(id=model_id).delete()

    def find_by_id(self, model_id):
        return self._model_class.objects.get(id=model_id)

    def filter(self, **kwargs):
        if self._qs is None:
            self._qs = self._model_class.objects.filter(**kwargs)
        else:
            self._qs = self._qs | self._model_class.objects.filter(**kwargs)
        return self

    def lazy_fetch(self):
        return self._qs

    def fetch_all(self):
        return self._qs.all()

    def fetch_related_all(self):
        return self._qs.select_related()

    def fetch(self):
        return self._qs.all().first()

    def fetch_related(self):
        return self._qs.select_related().first()


class ExamRepository(BaseRepository):

    def crate_model(self, questions, user):
        exam = self._model_class()
        exam.save()
        exam.questions.set([questions] if not isinstance(questions, col_abc.Iterable) else questions)
        exam.owner = user
        exam.save()
        return exam

    def update_model(self, model, **kwargs):
        try:
            exam = model
            if kwargs.get('questions'):
                exam.questions.set(kwargs.get('questions').all())
            exam.save()
        except ObjectDoesNotExist as e:
            raise InvalidParamError('Given exam id does not exist')
        return exam


class SolvedExamRepository(BaseRepository):

    def crate_model(self, exam, user):
        if self._model_class.objects.filter(exam=exam, user=user).count() > 0:
            raise SolvingError('Exam already solved by the user')

        return self._model_class.objects.create(exam=exam, user=user, date=datetime.now())

    def update_model(self, model, **kwargs):
        if kwargs.get('user') != model.exam.owner.username:
            raise PermissionDenied('Only user can grade')
        if kwargs.get('grade'):
            model.final_grade = float(kwargs.get('grade'))
        if kwargs.get('questions'):
            model.exam.questions.set(kwargs.get('questions').all())
        model.save()
        return model


class AnswerRepository(BaseRepository):

    def create_model(self, s_exam, question, value):
        answer = self._model_class()
        answer.solved_exam = s_exam
        answer.question = question
        answer.set_value(question.question_type, value)
        if question.question_type.type == QuestionTypeEnum.POSSIBILITY.value and question.correct_possibility.id == value:
            answer.solved_exam.possible_grade += question.max_grade
        if question.correct_answer == value:
            answer.solved_exam.possible_grade += question.max_grade
        answer.save()
        return answer
