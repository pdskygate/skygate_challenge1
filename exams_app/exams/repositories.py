import abc

from django.core.exceptions import ObjectDoesNotExist


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
    def find_by_id(self):
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
        self._model_class.objects.get(model_id).delete()

    def find_by_id(self):
        return self._model_class.objects.get(id)

    def filter(self, **kwargs):
        return self._model_class.objects.filter(**kwargs)


class ExamRepository(BaseRepository):

    def crate_model(self, questions, user):
        exam = self._model_class()
        exam.save()
        exam.questions = questions
        exam.owner = user
        exam.save()

    def update_model(self, model_id, **kwargs):
        try:
            exam = self._model_class.objects.get(model_id)
            exam.questions = kwargs.get('questions')
        except ObjectDoesNotExist as e:
            exam = self._model_class()
            exam.save()
            exam.questions = kwargs.get('questions')
            exam.owner = kwargs.get('user')
            exam.save()

