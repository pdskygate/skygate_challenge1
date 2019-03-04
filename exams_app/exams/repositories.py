import abc
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from collections import abc as col_abc

from rest_framework.exceptions import PermissionDenied

from exams_app.exams.exceptions import InvalidParamError, SolvingError
from exams_app.exams.models import Exam


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

    def crate_model(self, **kwargs):
        raise NotImplementedError('Cannot create, use specified repository')

    def update_model(self, model_id, **kwargs):
        raise NotImplementedError('Cannot update, use specified repository')

    def delete_model(self, model_id):
        self._model_class.objects.get(id=model_id).delete()

    def find_by_id(self, model_id):
        return self._model_class.objects.get(id=model_id)

    def filter(self, **kwargs):
        return self._model_class.objects.filter(**kwargs)

    def select_related(self, related_field, model_id):
        return self._model_class.objects.select_related(related_field).get(id=model_id)


class ExamRepository(BaseRepository):

    def crate_model(self, questions, user):
        exam = self._model_class()
        exam.save()
        exam.questions.set([questions] if not isinstance(questions, col_abc.Iterable) else questions)
        exam.owner = user
        exam.save()
        return exam

    def update_model(self, model_id, **kwargs):
        try:
            exam = self._model_class.objects.get(id=model_id)
            if kwargs.get('questions'):
                exam.questions.set([kwargs.get('questions')] if not isinstance(kwargs.get('questions'),
                                                                               col_abc.Iterable) else kwargs.get(
                    'questions'))
            exam.save()
        except ObjectDoesNotExist as e:
            raise InvalidParamError('Given exam id does not exist')
        return exam


class SolvedExamRepository(BaseRepository):

    def crate_model(self, exam, user):
        if self._model_class.objects.filter(exam=exam, user=user).count() > 0:
            raise SolvingError('Exam already solved by the user')

        self._model_class.objects.create(exam=exam, user=user, date=datetime.now())


    def update_model(self, model_id, **kwargs):
        solved_exam = self._model_class.objects.get(model_id)
        if kwargs.get('user') == solved_exam.exam.owner.username:
            raise PermissionDenied('Only user can grade')
        if kwargs.get('grade'):
            solved_exam.final_grade = kwargs.get('grade)')
        return solved_exam

class AnswerRepository(BaseRepository):


    def create_model(self, s_exam, question, value):
        answer = self._model_class()
        answer.solved_exam = s_exam
        answer.question = question
        answer.set_value(question.question_type, value)
        answer.save()
        return answer


