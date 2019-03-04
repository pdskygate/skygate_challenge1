from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from exams_app.exams.exceptions import InvalidParamError
from exams_app.exams.models import Exam, User, Question
from exams_app.exams.repositories import ExamRepository, BaseRepository
from exams_app.exams.response_builder import ResponseBuilder
from exams_app.exams.serializers import ExamSerializer


class ParamValidatorMixin(object):
    '''valid_definitins should be dict {param_name: type}'''

    valid_definitions = None

    def valid_params(self, actual_params):
        if not self.valid_definitions:
            raise APIException('Validation not definied')
        valid_names = [name for name, type in self.valid_definitions.items()]
        actual_names = actual_params.keys()
        if len(set(actual_names) - set(valid_names)) > 0:
            raise InvalidParamError(f'Valid params {valid_names} , given params {actual_names}')
        for key, value in actual_params.items():
            try:
                self.valid_definitions.get(key)(value)
            except:
                raise InvalidParamError(f'Invalid type param. {key}, should be {self.valid_definitions.get(key)}')
        return True


class ExamManagementView(viewsets.ModelViewSet, ParamValidatorMixin):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BasicAuthentication,)
    serializer_class = ExamSerializer
    valid_definitions = {

    }

    def get_queryset(self):
        pass

    def list(self, request, **kwargs):

        pass

    def create(self, request, *args, **kwargs):
        self.valid_definitions.update({'q': list})
        params = request.POST.dict()
        params.update({'q': request.POST.getlist('q')})
        self.valid_params(params)

        exam_repo = ExamRepository(Exam)
        user_repo = BaseRepository(User)
        q_repo = BaseRepository(Question)
        try:
            for question_id in params.get('q'):
                q_repo.find_by_id(question_id)
        except Question.DoesNotExist as e:
            raise InvalidParamError(f'Question {e}, does not exist')
        user = user_repo.filter(username=request.user).first()

        exam = exam_repo.crate_model(user=user, questions=params.get('q'))

        return ResponseBuilder(self.serializer_class(exam).data).build()

    def update(self, request, *args, **kwargs):
        pass
