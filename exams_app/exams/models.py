from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class QuestionTypeEnum(Enum):
    TEXT = 'text'
    NUMBER = 'number'
    POSSIBILITY = 'select'
    BOOLEAN = 'boolean'


class User(AbstractUser):

    user = models.BooleanField('ordinary user of service', default=True)
    reviewer = models.BooleanField('user that can change ', default=False)


class AnswerPossibility(models.Model):
    class Meta:
        verbose_name = _('Answer possibility')
        verbose_name_plural = _('Answer possibilities')

    code = models.CharField(max_length=20)
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.value


class QuestionType(models.Model):
    class Meta:
        verbose_name = _(u'Answer type')
        verbose_name_plural = _(u'Answer types')

    type = models.CharField(max_length=15)


class Question(models.Model):
    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')

    text = models.CharField(max_length=250, null=True, blank=True)
    question_type = models.ForeignKey(QuestionType, on_delete=models.CASCADE, null=True, blank=True)

    answer_possibilities = models.ManyToManyField(AnswerPossibility, blank=True)
    correct_answer = models.CharField(max_length=300, blank=True, null=True)
    correct_possibility = models.ForeignKey(AnswerPossibility, null=True, blank=True, on_delete=models.DO_NOTHING,
                                            related_name='related_question')
    max_grade = models.FloatField(default=5, null=True)

    def is_correct(self, value):
        if isinstance(value, bool):
            return (True if self.correct_answer.lower() == 'yes' else False) and value
        return str(value).lower() == self.correct_answer.lower()

    def __str__(self):
        return self.text


class Exam(models.Model):
    class Meta:
        verbose_name = _('Exam')
        verbose_name_plural = _('Exam')

    questions = models.ManyToManyField(Question, verbose_name=("Exams tasks"))
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.DO_NOTHING)


class SolvedExam(models.Model):
    class Meta:
        verbose_name = _('Solved Exam')
        verbose_name_plural = _('Solved_exams')

    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    final_grade = models.FloatField(blank=True, null=True)
    possible_grade = models.FloatField(default=0)


class Answer(models.Model):
    class Meta:
        verbose_name = _(u'Answer')
        verbose_name_plural = _(u'Answers')

    solved_exam = models.ForeignKey(SolvedExam, on_delete=models.CASCADE, null=True, blank=True)
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING)
    text_answer = models.CharField(max_length=250, null=True, blank=True)
    binary_answer = models.NullBooleanField(null=True, blank=True)
    number_value = models.FloatField(null=True, blank=True)
    chosen_value = models.ForeignKey(AnswerPossibility, null=True, blank=True, on_delete=models.SET_NULL)

    def get_value(self):
        try:
            a_type = self.question.question_type.type
            if a_type == QuestionTypeEnum.TEXT.value:
                return self.text_answer
            elif a_type == QuestionTypeEnum.BOOLEAN.value:
                return str(self.binary_answer)
            elif a_type == QuestionTypeEnum.NUMBER.value:
                return str(self.number_value)
            else:
                return self.chosen_value
        except Question.DoesNotExist:
            return ''

    def set_value(self, type, value):
        type = type.type
        if type == QuestionTypeEnum.TEXT.value:
            self.text_answer = value
        elif type == QuestionTypeEnum.BOOLEAN.value:
            self.binary_answer = value
        elif type == QuestionTypeEnum.NUMBER.value:
            self.number_value = value
        else:
            self.chosen_value = AnswerPossibility.objects.get(id=int(value))

    def __str__(self):
        return self.get_value()
