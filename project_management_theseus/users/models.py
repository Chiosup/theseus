from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('manager', 'Менеджер'),
        ('employee', 'Сотрудник'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')
    def save(self, *args, **kwargs):
        """Автоматически задаем is_staff в зависимости от роли"""
        if self.role == 'admin':
            self.is_staff = True
            self.is_superuser = True  # Администраторы имеют полный доступ
        else:
            self.is_staff = False  # Запрещаем доступ к админке для менеджеров и сотрудников
            self.is_superuser = False
        super().save(*args, **kwargs)