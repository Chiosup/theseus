# Generated by Django 5.1.6 on 2025-02-13 13:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('start_date', models.DateField(verbose_name='Дата начала')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Дата окончания')),
                ('status', models.CharField(choices=[('active', 'Активный'), ('completed', 'Завершен')], default='active', max_length=20, verbose_name='Статус')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_projects', to=settings.AUTH_USER_MODEL, verbose_name='Создатель')),
                ('participants', models.ManyToManyField(related_name='projects', to=settings.AUTH_USER_MODEL, verbose_name='Участники')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('due_date', models.DateField(verbose_name='Срок выполнения')),
                ('status', models.CharField(choices=[('new', 'Новая'), ('in_progress', 'В процессе'), ('done', 'Выполнена')], default='new', max_length=20, verbose_name='Статус')),
                ('priority', models.CharField(choices=[('low', 'Низкий'), ('medium', 'Средний'), ('high', 'Высокий')], default='medium', max_length=10, verbose_name='Приоритет')),
                ('assigned_to', models.ManyToManyField(related_name='tasks', to=settings.AUTH_USER_MODEL, verbose_name='Исполнители')),
                ('previous_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='next_task', to='projects.task', verbose_name='Предыдущая задача')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='projects.project', verbose_name='Проект')),
            ],
        ),
    ]
