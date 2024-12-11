from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('tutorials', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='frequency',
            field=models.CharField(choices=[('W', 'Weekly'), ('B', 'Biweekly'), ('M', 'Monthly'), ('O', 'Once')], max_length=10),
        ),
        migrations.AlterField(
            model_name='lessonrequest',
            name='frequency',
            field=models.CharField(choices=[('W', 'Weekly'), ('B', 'Biweekly'), ('M', 'Monthly'), ('O', 'Once')], max_length=10),
        ),
    ]
