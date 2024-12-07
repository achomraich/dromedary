# Generated by Django 5.1.2 on 2024-12-07 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lessonrequest',
            name='day',
            field=models.CharField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')], max_length=3),
        ),
        migrations.AlterField(
            model_name='tutoravailability',
            name='day',
            field=models.CharField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')], max_length=15),
        ),
        migrations.AlterUniqueTogether(
            name='tutoravailability',
            unique_together={('tutor', 'day', 'start_time', 'end_time')},
        ),
    ]
