from collections import Iterable
from datetime import datetime

from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from exams_app.exams.exceptions import InvalidParamError
from exams_app.exams.models import Exam, User, Question, SolvedExam, Answer, QuestionTypeEnum
from exams_app.exams.response_builder import ResponseBuilder, BasePaginator
from exams_app.exams.serializers import ExamSerializer, SolvedExamSerializer, AnswerSerializer, QuestionSerializer


class MultiQuestionQS(object):

    valid_definitions = None

    def build_multiple_question_qs(self, question_id):
        qs = None
        for q_id in question_id:
            if not qs:
                qs = Question.objects.filter(pk=q_id)
            else:
                qs = qs.union(Question.objects.filter(pk=q_id))
        return qs

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


class ExamManagementView(viewsets.ModelViewSet, MultiQuestionQS):
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
            paginated_qs = paginator.paginate_queryset(Exam.objects.filter(**params).select_related(),
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

        for question_id in params.get('q'):
            if Question.objects.filter(pk=question_id).count() == 0:
                raise InvalidParamError(f'Question with id does not exist {question_id}')

        user = User.objects.get(username=request.user)
        exam = Exam()
        exam.owner = user
        exam.save()
        exam.questions.set([params.get('q')] if not isinstance(params.get('q'), Iterable) else params.get('q'))
        exam.save()
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
        exam = Exam.objects.select_related().get(id=params.pop('pk'))
        if request.user.username != exam.owner.username:
            raise PermissionDenied('Only owner can grade')
        questions = params.get('q')
        if questions:
            exam.questions.set(self.build_multiple_question_qs(questions).all())
        return ResponseBuilder(self.serializer_class(exam).data).build()

    # /exam/{pk}/
    def destroy(self, request, **kwargs):
        exam_id = self.kwargs.get('pk')
        try:
            exam = Exam.objects.select_related().get(pk=exam_id)
            if request.user.username != exam.owner.username:
                raise PermissionDenied('Only owner can delete')
            exam.delete()
        except Exam.DoesNotExist as e:
            raise InvalidParamError('Exam with given id not exists')
        return ResponseBuilder(True).build()


class SolveExamView(viewsets.ModelViewSet, MultiQuestionQS):
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
        answers = Answer.objects.filter(solved_exam__exam_id=params.get('exam_id'),
                                        solved_exam__user__username=params.get(
                                            'user_name')).select_related().all()

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

        exam = Exam.objects.select_related().get(pk=params.get('exam_id'))
        solved = SolvedExam()#.crate_model(exam=exam, user=request.user)
        solved.exam = exam
        solved.user = request.user
        solved.date = datetime.now()
        solved.save()
        for question in exam.questions.all():
            a = Answer()
            a.solved_exam = solved
            a.question = question
            value = params.get('answers').get(str(question.id), '')
            a.set_value(question.question_type, value)
            if question.question_type.type == QuestionTypeEnum.POSSIBILITY.value:
                if question.correct_possibility.id == value:
                    a.solved_exam.possible_grade += question.max_grade
            else:
                if question.is_correct(value):
                    a.solved_exam.possible_grade += question.max_grade
            a.save()
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
        solved_exam = SolvedExam.objects.select_related().get(pk=params.get('pk'))
        if request.user.username != solved_exam.exam.owner.username:
            raise PermissionDenied('Only owner can grade')
        if params.get('final_grade'):
            solved_exam.final_grade = float(params.get('final_grade'))
        solved_exam.save()
        return ResponseBuilder(self.serializer_class(solved_exam).data).build()


class QuestionView(viewsets.ModelViewSet, MultiQuestionQS):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BasicAuthentication,)
    serializer_class = QuestionSerializer
    valid_definitions = {

    }

    def get_queryset(self):
        return Question.objects.all()

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
        paginated = paginator.paginate_queryset(self.get_queryset().select_related(), request)
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
        # repo = BaseRepository(Question)
        question = Question.objects.get(pk=params.get('pk'))
        if params.get('max_grade'):
            question.max_grade=params.get('max_grade')
        one_of_poss = bool(params.get('one_of_poss'))
        correct_a = params.get('correct_answer')
        if one_of_poss:
            try:
                correct_a = int(correct_a)
            except ValueError as e:
                raise InvalidParamError('One of possible answer have to be an int')

            question.correct_possibility = correct_a
        elif correct_a:
            question.correct_answer = correct_a
        return ResponseBuilder(self.serializer_class(question).data).build()
