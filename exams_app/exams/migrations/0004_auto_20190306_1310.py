# Generated by Django 2.1.7 on 2019-03-06 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0003_auto_20190304_2236'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='correct_answer',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='max_grade',
            field=models.FloatField(default=5),
        ),
        migrations.AddField(
            model_name='solvedexam',
            name='possible_grade',
            field=models.FloatField(default=0),
        ),
    ]