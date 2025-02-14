from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Project, Task
from .forms import ProjectForm, TaskForm
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
import json

@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, creator=request.user)  # Только менеджер может редактировать
    
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)

    return render(request, 'projects/edit_project.html', {'form': form, 'project': project})
@login_required
def project_list(request):
    """Отображение списка проектов, в которых участвует пользователь или которые он создал."""
    if request.user.is_superuser:
        projects = Project.objects.all()  # Админ видит все проекты
    elif request.user.groups.filter(name="Менеджеры").exists():
        projects = Project.objects.filter(creator=request.user)  # Менеджеры видят свои проекты
    else:
        projects = Project.objects.filter(participants=request.user)  # Остальные видят, где участвуют

    # Добавляем атрибут с количеством завершенных задач
    for project in projects:
        project.completed_tasks_count = project.tasks.filter(status="completed").count()

    return render(request, "projects/project_list.html", {"projects": projects})

@login_required
def project_detail(request, project_id):
    """Отображение деталей проекта и списка задач в нем."""
    project = get_object_or_404(Project, id=project_id)
    tasks = project.tasks.all().order_by("due_date")

    tasks_data = []
    for task in tasks:
        tasks_data.append({
            "id": task.id,
            "name": task.title,
            "start": task.start_date.strftime("%Y-%m-%d") if task.start_date else None,
            "end": task.end_date.strftime("%Y-%m-%d") if task.end_date else None,
            "progress": 100 if task.status == "done" else (50 if task.status == "in_progress" else 0)
        })

    tasks_json = json.dumps(tasks_data, ensure_ascii=False)  # Генерация JSON

    print("DEBUG JSON:", tasks_json)  # Выведи в консоль сервера для отладки

    return render(request, 'projects/project_detail.html', {
        "project": project,
        "tasks": tasks,  # Передаем задачи для списка
        "tasks_json": tasks_json  # Передаем JSON для диаграммы Ганта
    })

@login_required
def create_project(request):
    if not request.user.groups.filter(name="Менеджеры").exists():  # Или другой способ проверки
        raise PermissionDenied("У вас нет прав для создания проекта.")
    
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.creator = request.user  # Назначаем создателя проекта
            project.save()
            form.save_m2m()  # Сохраняем участников
            return redirect('project_list')
    else:
        form = ProjectForm()

    return render(request, "projects/create_project.html", {"form": form})

@login_required
def create_task(request, project_id):
    """Создание новой задачи в проекте (только для менеджеров)."""
    project = get_object_or_404(Project, id=project_id)

    if not request.user.groups.filter(name="Менеджеры").exists():
        return redirect('project_detail', project_id=project.id)

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)

            # Устанавливаем даты, если их нет
            if not task.start_date:
                task.start_date = now().date()
            if not task.end_date:
                task.end_date = task.start_date + timedelta(days=7)
            task.due_date = task.end_date  # Устанавливаем due_date = end_date

            task.project = project
            task.save()
            form.save_m2m()  # Сохранение исполнителей
            return redirect('project_detail', project_id=project.id)
    else:
        form = TaskForm()

    return render(request, 'projects/task_form.html', {'form': form, 'project': project})


@login_required
def update_task_status(request, task_id):
    """Обновление статуса задачи (только для исполнителей задачи)."""
    task = get_object_or_404(Task, id=task_id)

    if request.user not in task.assignee.all():
        return redirect('project_detail', project_id=task.project.id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in ['new', 'in_progress', 'done']:
            task.status = new_status
            if new_status == 'done':
                task.completed_by = request.user
            task.save()
    
    return redirect('project_detail', project_id=task.project.id)
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, "projects/task_detail.html", {"task": task})

@login_required
def start_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.status == "new":
        task.status = "in_progress"
        task.save()
    return redirect("project_detail", project_id=task.project.id)

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.status == "in_progress":
        task.status = "done"
        task.save()
    return redirect("project_detail", project_id=task.project.id)
def revert_to_pending(request, task_id):
    """Откатывает задачу из 'in_progress' обратно в 'pending'."""
    task = get_object_or_404(Task, id=task_id)
    if task.status == 'in_progress':  
        task.status = 'new'
        task.save()
    return redirect('task_detail', task_id=task.id)

def revert_to_in_progress(request, task_id):
    """Откатывает задачу из 'completed' обратно в 'in_progress'."""
    task = get_object_or_404(Task, id=task_id)
    if task.status == 'done':  
        task.status = 'in_progress'
        task.save()
    return redirect('task_detail', task_id=task.id)