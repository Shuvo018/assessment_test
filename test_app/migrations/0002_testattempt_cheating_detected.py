# Generated migration to add cheating_detected field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='testattempt',
            name='cheating_detected',
            field=models.BooleanField(default=False),
        ),
    ]
