# Generated by Django 5.1.2 on 2024-12-02 21:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lessonrequest',
            old_name='lesson_day',
            new_name='day',
        ),
        migrations.RenameField(
            model_name='lessonrequest',
            old_name='request_id',
            new_name='request',
        ),
        migrations.RenameField(
            model_name='lessonrequest',
            old_name='student_id',
            new_name='student',
        ),
        migrations.RenameField(
            model_name='lessonrequest',
            old_name='subject_id',
            new_name='subject',
        ),
        migrations.RenameField(
            model_name='lessonrequest',
            old_name='term_id',
            new_name='term',
        ),
        migrations.RenameField(
            model_name='lessonrequest',
            old_name='lesson_time',
            new_name='time',
        ),
    ]