# Generated by Django 5.1.6 on 2025-03-27 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('admin', 'Администратор'), ('director', 'Руководитель'), ('manager', 'Менеджер'), ('employee', 'Сотрудник')], default='employee', max_length=10),
        ),
    ]
