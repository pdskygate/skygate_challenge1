import logging

from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("exceptions")


class InvalidParamError(APIException):
    status_code = 400


class ModelNotExistsError(APIException):
    status_code = 400


class SolvingError(APIException):
    status_code = 400


def api_exception_chandler(exc, context):
    response = exception_handler(exc, context)
    logger.error(exc, exc_info=(type(exc), exc, exc.__traceback__))
    if response is not None:
        response.data['status_code'] = response.status_code
    else:
        response = Response()
        response.data = {"status_code": 500, "detail": str(exc)}
    return response
