# Generated by Django 2.2.10 on 2020-02-17 22:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20200217_1530'),
    ]

    operations = [
        migrations.AddField(
            model_name='park',
            name='garage',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='api.Garage'),
            preserve_default=False,
        ),
    ]