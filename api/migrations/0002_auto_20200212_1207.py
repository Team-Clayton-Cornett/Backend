# Generated by Django 2.2.10 on 2020-02-12 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='day_of_week',
            field=models.CharField(choices=[('SU', 'Sunday'), ('MO', 'Monday'), ('TU', 'Tuesday'), ('WE', 'Wednesday'), ('TH', 'Thursday'), ('FR', 'Friday'), ('SA', 'Saturday')], default='MO', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dayprobability',
            name='day_of_week',
            field=models.CharField(choices=[('SU', 'Sunday'), ('MO', 'Monday'), ('TU', 'Tuesday'), ('WE', 'Wednesday'), ('TH', 'Thursday'), ('FR', 'Friday'), ('SA', 'Saturday')], max_length=10),
        ),
    ]