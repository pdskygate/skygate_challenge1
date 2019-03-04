from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated

from exams_app.exams.exceptions import InvalidParamError
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
        'test': int
    }

    def get_queryset(self):
        pass

    def list(self, request, **kwargs):
        self.valid_params(request.GET.dict())
        pass

    def create(self, request, *args, **kwargs):
        pass

    def update(self, request, *args, **kwargs):
        pass
