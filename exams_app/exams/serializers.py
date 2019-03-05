from rest_framework import serializers

from exams_app.exams.models import QuestionType, AnswerPossibility, Question, Answer, User, Exam, SolvedExam


class QuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionType
        fields = ('type',)


class AnswerPossibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerPossibility
        fields = ('code', 'value')


class QuestionSerializer(serializers.ModelSerializer):
    question_type = QuestionTypeSerializer()
    answer_possibilities = AnswerPossibilitySerializer(many=True)

    class Meta:
        model = Question
        fields = ('text', 'question_type', 'answer_possibilities')


class AnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()
    chosen_value = AnswerPossibilitySerializer()

    class Meta:
        model = Answer
        fields = ('number_value', 'binary_answer', 'text_answer')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk',)


class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(read_only=True, many=True)
    owner = UserSerializer()

    class Meta:
        model = Exam
        fields = ('questions', 'owner','pk')

class SolvedExamSerializer(serializers.ModelSerializer):


    class Meta:
        model = SolvedExam
        fields = ('pk','final_grade', )