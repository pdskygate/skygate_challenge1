from rest_framework import serializers

from exams_app.exams.models import QuestionType, AnswerPossibility, Question, Answer, User, Exam


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
        fields = ('text',)


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
    questions = QuestionSerializer()
    owner = UserSerializer()

    class Meta:
        model = Exam
        fields = ('final_grade',)
