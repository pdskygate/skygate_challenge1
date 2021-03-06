# Generated by Django 2.1.7 on 2019-03-06 18:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0006_auto_20190306_1440'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='question',
            name='answer_possibilities',
            field=models.ManyToManyField(blank=True, to='exams.AnswerPossibility'),
        ),
    ]
