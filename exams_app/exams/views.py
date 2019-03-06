from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from exams_app.exams.exceptions import InvalidParamError
from exams_app.exams.models import Exam, User, Question, SolvedExam, Answer
from exams_app.exams.repositories import ExamRepository, BaseRepository, SolvedExamRepository, AnswerRepository
from exams_app.exams.response_builder import ResponseBuilder, BasePaginator
from exams_app.exams.serializers import ExamSerializer, SolvedExamSerializer, AnswerSerializer, QuestionSerializer


class ParamValidatorMixin(object):
    '''valid_definitins should be dict {param_name: type}'''

    valid_definitions = None

    def valid_params(self, actual_params):
        if 'page' in actual_params:
            actual_params.pop('page')
        if 'page_size' in actual_params:
            actual_params.pop('page_size')
        if not self.valid_definitions:
            raise APIException('Validation not definied')
        valid_names = [name for name, type in self.valid_definitions.items()] + ['csrfmiddlewaretoken']
        actual_names = list(actual_params.keys())
        if len(set(actual_names) - set(valid_names)) > 0:
            raise InvalidParamError(f'Valid params {valid_names} , given params {actual_names}')
        for key, value in actual_params.items():
            try:
                self.valid_definitions.get(key)(value)
            except:
                raise InvalidParamError(f'Invalid type param. {key}, should be {self.valid_definitions.get(key)}')
        return True


class ExamManagementView(viewsets.ModelViewSet, ParamValidatorMixin):
    serializer_class = ExamSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BasicAuthentication,)
    valid_definitions = {

    }

    def get_queryset(self):
        return Exam.objects.all()

    # exam?page_size = 10 mandatory
    def list(self, request, **kwargs):
        self.valid_definitions.update({
            'id': int,
            'page_size': int,
            'page': int
        })

        params = request.query_params.dict()
        self.valid_params(params)
        try:
            paginator = BasePaginator()
            if params.get('page_size'):
                paginator.page_size = params.get('page_size')
            paginated_qs = paginator.paginate_queryset(ExamRepository(Exam).filter(**params).fetch_related_all(),
                                                       request)
            return ResponseBuilder(
                self.serializer_class(paginated_qs, many=True).data, paginator
            ).paginated_response().build()
        except Exam.DoesNotExist as e:
            raise InvalidParamError(f'Exam {e}, does not exist')

    # {
    #  "q": [1,2,3]
    # }
    def create(self, request, *args, **kwargs):
        self.valid_definitions.update({'q': list})
        params = request.data
        self.valid_params(params)

        exam_repo = ExamRepository(Exam)
        user_repo = BaseRepository(User)
        q_repo = BaseRepository(Question)
        try:
            for question_id in params.get('q'):
                q_repo.find_by_id(question_id)
        except Question.DoesNotExist as e:
            raise InvalidParamError(f'Question {e}, does not exist')
        user = user_repo.filter(username=request.user).fetch()

        exam = exam_repo.crate_model(user=user, questions=params.get('q'))

        return ResponseBuilder(self.serializer_class(exam).data).build()

    # {
    #     "q": [1]
    # }
    def update(self, request, *args, **kwargs):
        self.valid_definitions.update({
            'q': list,
            'pk': int
        })
        params = {
            'pk': self.kwargs.get('pk')
        }
        params.update(request.data)
        self.valid_params(params)
        exam_repo = ExamRepository(Exam)
        exam = exam_repo.filter(id=params.pop('pk')).fetch_related()
        questions = params.get('q')
        q_repo = BaseRepository(Question)
        if questions:
            for q_id in questions:
                q_repo.filter(id=q_id)
            exam = exam_repo.update_model(exam, user=request.user.username, questions=q_repo.fetch_all())
        return ResponseBuilder(self.serializer_class(exam).data).build()

    # /exam/{pk}/
    def destroy(self, request, **kwargs):
        exam_repo = ExamRepository(Exam)
        exam_id = self.kwargs.get('pk')
        try:
            exam_repo.delete_model(exam_id, user=request.user.username)
        except Exam.DoesNotExist as e:
            raise InvalidParamError('Exam with given id not exists')

        return ResponseBuilder(True).build()


class SolveExamView(viewsets.ModelViewSet, ParamValidatorMixin):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BasicAuthentication,)
    serializer_class = SolvedExamSerializer
    valid_definitions = {

    }

    def get_queryset(self):
        return Answer.objects.all()

    # solve_exam?exam_id=3&user_name=admin
    def list(self, request, *args, **kwargs):
        self.valid_definitions.update({
            'user_name': str,
            'exam_id': int,
            'page_size': int,
            'page': int
        })
        params = request.query_params.dict()
        answers = AnswerRepository(Answer).filter(solved_exam__exam_id=params.get('exam_id'),
                                                  solved_exam__user__username=params.get(
                                                      'user_name')).fetch_related_all()
        return ResponseBuilder(AnswerSerializer(answers, many=True).data).build()

    # {
    # 	"exam_id":24,
    # 	"answers": {"1":1}
    # }
    def create(self, request, *args, **kwargs):
        # contract agreement should be more strict
        self.valid_definitions.update({
            'exam_id': int,
            'answers': dict,
        })
        params = request.data
        self.valid_params(params)
        solvedE_repo = SolvedExamRepository(SolvedExam)
        exam = ExamRepository(Exam).filter(id=params.get('exam_id')).fetch_related()
        solved = solvedE_repo.crate_model(exam=exam, user=request.user)
        for question in exam.questions.all():
            AnswerRepository(Answer).create_model(solved, question, params.get('answers').get(str(question.id), ''))

        return ResponseBuilder(f'Exam solved, wait for graduation. Possible result {solved.possible_grade}').build()

    # {
    # "final_grade":24
    # }
    #
    def update(self, request, *args, **kwargs):
        # contract agreement should be more strict
        self.valid_definitions.update({
            'pk': int,
            'final_grade': float
        })
        params = {
            'pk': self.kwargs.get('pk')
        }
        params.update(request.data)
        self.valid_params(params)
        solvedE_repo = SolvedExamRepository(SolvedExam)
        solved_exam = solvedE_repo.filter(id=params.get('pk')).fetch_related()
        if params.get('final_grade'):
            solvedE_repo.update_model(solved_exam, user=request.user.username, grade=params.get('final_grade'))
        return ResponseBuilder(self.serializer_class(solved_exam).data).build()


class QuestionView(viewsets.ModelViewSet, ParamValidatorMixin):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BasicAuthentication,)
    serializer_class = QuestionSerializer
    valid_definitions = {

    }

    def get_queryset(self):
        return BaseRepository(Question).filter()

    # /question?page_size=2
    def list(self, request, *args, **kwarg):
        self.valid_definitions.update({
            'id': int,
            'page_size': int,
            'page': int
        })

        params = request.query_params.dict()
        self.valid_params(params)
        paginator = BasePaginator()
        if params.get('page_size'):
            paginator.page_size = params.get('page_size')
        paginated = paginator.paginate_queryset(self.get_queryset().fetch_related_all(), request)
        return ResponseBuilder(
            self.serializer_class(paginated, many=True).data, paginator
        ).paginated_response().build()


class QuestionUpdateView(QuestionView):
    permission_classes = (IsAdminUser,)
    authentication_classes = (BasicAuthentication,)
    serializer_class = QuestionSerializer
    valid_definitions = {

    }

    # {
    #    "max_grade": 12,
    #    "correct_answer": 1,
    #    "one_of_poss": true
    # }
    def update(self, request, *args, **kwargs):
        self.valid_definitions.update({
            'max_grade': float,
            'correct_answer': str,
            'one_of_poss': bool,
            'pk': int
        })
        params = request.data
        params.update({'pk': self.kwargs.get('pk')})
        self.valid_params(params)
        repo = BaseRepository(Question)
        question = repo.find_by_id(params.get('pk'))
        if params.get('max_grade'):
            repo.update_model(question, max_grade=params.get('max_grade'))
        one_of_poss = bool(params.get('one_of_poss'))
        correct_a = params.get('correct_answer')
        if one_of_poss:
            try:
                correct_a = int(correct_a)
            except ValueError as e:
                raise InvalidParamError('One of possible answer have to be an int')

            question = repo.update_model(question, correct_possibility_id=correct_a)
        elif correct_a:
            question = repo.update_model(question, correct_answer=correct_a)
        return ResponseBuilder(self.serializer_class(question).data).build()
