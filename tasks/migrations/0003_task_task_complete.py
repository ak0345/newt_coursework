# Generated by Django 4.2.7 on 2023-11-06 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0002_task_user_owned_tasks"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="task_complete",
            field=models.BooleanField(default=False),
        ),
    ]