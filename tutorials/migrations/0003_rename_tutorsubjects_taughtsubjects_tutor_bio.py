# Generated by Django 5.1.2 on 2024-12-02 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0002_alter_lessonrequest_language_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TutorSubjects',
            new_name='TaughtSubjects',
        ),
        migrations.AddField(
            model_name='tutor',
            name='bio',
            field=models.TextField(blank=True),
        ),
    ]