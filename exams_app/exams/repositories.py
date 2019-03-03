import abc

from django.core.exceptions import ObjectDoesNotExist
from collections import abc as col_abc


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

            exam.questions.set([kwargs.get('questions')] if not isinstance(kwargs.get('questions'), col_abc.Iterable) else kwargs.get('questions'))
            exam.save()
        except ObjectDoesNotExist as e:
            exam = self._model_class()
            exam.save()
            exam.questions.set([kwargs.get('questions')] if not isinstance(kwargs.get('questions'), col_abc.Iterable) else kwargs.get('questions'))
            exam.owner = kwargs.get('user')
            exam.save()
        return exam

