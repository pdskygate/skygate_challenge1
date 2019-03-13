from django.test import TestCase

from exams_app.exams.exceptions import InvalidParamError
from exams_app.exams.views import ParamValidatorMixin


class ParamValidationTestCase(TestCase):

    def test_valid_params(self):
        # given
        test_params = {
            'length': 10
        }
        test_definitions = {
            'length':int
        }
        validator = ParamValidatorMixin()
        validator.valid_definitions = test_definitions
        #when
        #then
        self.assertTrue(validator.valid_params(test_params))



    def test_not_known_name(self):
        # given
        test_params = {
            'length': 10
        }
        test_definitions = {
            'width': int
        }
        validator = ParamValidatorMixin()
        validator.valid_definitions = test_definitions
        # when
        # then
        self.assertRaises(InvalidParamError, validator.valid_params, test_params)


    def test_wrong_type(self):
        # given
        test_params = {
            'length': 10
        }
        test_definitions = {
            'width': str
        }
        validator = ParamValidatorMixin()
        validator.valid_definitions = test_definitions
        # when
        # then
        self.assertRaises(InvalidParamError, validator.valid_params, test_params)
