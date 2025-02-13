from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Project, Task
from .forms import ProjectForm, TaskForm
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied


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

    return render(request, 'projects/project_detail.html', {'project': project, 'tasks': tasks})

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
        if new_status in ['new', 'in_progress', 'completed']:
            task.status = new_status
            if new_status == 'completed':
                task.completed_by = request.user
            task.save()
    
    return redirect('project_detail', project_id=task.project.id)