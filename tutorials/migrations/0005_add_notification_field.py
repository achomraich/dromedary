from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('tutorials', '0004_merge_notification_migrations'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='has_new_lesson_notification',
            field=models.BooleanField(default=False),
        ),
    ]
