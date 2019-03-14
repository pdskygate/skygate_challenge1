from django.core.management import BaseCommand

from exams_app.exams.models import User, Exam, Question
import logging

logger = logging.getLogger('exceptions')

class Command(BaseCommand):
    help = "Create some initial data"


    def handle(self, *args, **kwargs):

        try:
            admin = User.objects.create_superuser(username='superuser', password='user', email='test@gmail.com')
            u1 = User.objects.create_user(username='user1', password='user', reviewer=True)
            u2 = User.objects.create_user(username='user2', password='user')
            u3 = User.objects.create_user(username='user3', password='user')

            e1 = Exam()
            e1.owner = u1
            e1.save()
            e1.questions.set(Question.objects.all()[1:3])

            e2 = Exam()
            e2.owner = u2
            e2.save()
            e2.questions.set(Question.objects.all()[2:4])

            e3 = Exam()
            e3.owner = u3
            e3.save()
            e3.questions.set(Question.objects.all())

        except Exception as e:
            logger.error("cannot load initial data", exc_info=(type(e), e, e.__traceback__))

