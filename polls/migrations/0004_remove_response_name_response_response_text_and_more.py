# Generated by Django 5.2.3 on 2025-06-23 15:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_response'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='response',
            name='name',
        ),
        migrations.AddField(
            model_name='response',
            name='response_text',
            field=models.CharField(default='null', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='response',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses_from_responses_app', to='polls.question'),
        ),
    ]
