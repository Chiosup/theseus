from django.urls import path
from . import views  # Убедись, что импортируется views из текущего приложения

urlpatterns = [
    path('', views.project_list, name='project_list'),  
    path('<int:project_id>/', views.project_detail, name='project_detail'),
    path('create/', views.create_project, name='create_project'),
    path('<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('<int:project_id>/tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/update_status/', views.update_task_status, name='update_task_status'),
]
