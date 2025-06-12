from django.shortcuts import render, redirect, get_object_or_404
# from django.views.generic import ListView
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Task, ProgressTracking
from .forms import TaskForm, TaskUpdateForm, ProgressTrackingForm

def task_list(request):
    # 默认过滤掉已关闭和已取消的任务 - 使用values()减少查询字段
    tasks = Task.objects.filter(
        ~Q(status='CLOSED') & ~Q(status='CANCELLED')
    ).order_by('project', '-proposed_date').values(
        'id', 'task_id', 'name', 'proposer', 'executor', 
        'project', 'related_code', 'related_name', 'status', 'priority'
    )

    # 处理筛选条件
    proposer = request.GET.get('proposer')
    executor = request.GET.get('executor')
    project = request.GET.get('project')
    status = request.GET.get('status')
    priority = request.GET.get('priority')
        
    if proposer:
        tasks = tasks.filter(proposer=proposer)
    if executor:
        tasks = tasks.filter(executor=executor)
    if project:
        tasks = tasks.filter(project=project)
    if status:
        tasks = tasks.filter(status=status)
    if priority:
        tasks = tasks.filter(priority=priority)

    # 优化筛选选项获取 - 使用distinct()和values_list
    proposers = Task.objects.order_by('proposer').values_list('proposer', flat=True).distinct()
    executors = Task.objects.order_by('executor').values_list('executor', flat=True).distinct()
    projects = Task.objects.order_by('project').values_list('project', flat=True).distinct()
    statuses = Task.STATUS_CHOICES
    priorities = Task.PRIORITY_CHOICES

    # 使用分组字典代替regroup
    grouped_tasks = {}
    for task in tasks:
        project_name = task['project']
        if project_name not in grouped_tasks:
            grouped_tasks[project_name] = []
        grouped_tasks[project_name].append(task)

    # 分页处理 - 按项目分组分页
    page_size = 5  # 每页显示的项目组数
    paginator = Paginator(list(grouped_tasks.items()), page_size)
    page = request.GET.get('page')   
    try:
        page_groups = paginator.page(page)
    except PageNotAnInteger:
        page_groups = paginator.page(1)
    except EmptyPage:
        page_groups = paginator.page(paginator.num_pages)

    return render(request, 'tasks/task_list.html', {
        'tasks': tasks,
        'proposers': proposers,
        'executors': executors,
        'projects': projects,
        'statuses': statuses,
        'priorities': priorities,
        'filter_params': request.GET
    })

def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            # 自动生成task_id的逻辑现在在模型的save方法中
            task = form.save()
            messages.success(request, '任务创建成功!')
            return redirect('tasks:task_list')
        else:
            messages.error(request, '请修正以下错误')
    else:
        # 为新表单设置初始值
        initial_data = {'proposed_date': timezone.now(),}
        form = TaskForm(initial=initial_data)
    
    return render(request, 'tasks/task_create.html', {'form': form})

def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    progress_list = task.progress_trackings.all().order_by('-update_date')

    if request.method == 'POST':
        form = TaskUpdateForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, '协作信息更新成功!')
            return redirect('tasks:task_detail', pk=task.pk)
    else:
        form = TaskUpdateForm(instance=task)

    return render(request, 'tasks/task_detail.html', {
        'task': task,
        'form': form,
        'progress_list': progress_list
    })

def progress_create(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    
    if request.method == 'POST':
        form = ProgressTrackingForm(request.POST)
        if form.is_valid():
            progress = form.save(commit=False)
            progress.task = task
            progress.related_object_code = task.task_id
            progress.save()
            messages.success(request, '进度信息添加成功!')
            return redirect('tasks:task_detail', pk=task.pk)
    else:
        form = ProgressTrackingForm()
    
    return render(request, 'tasks/progress_create.html', {
        'form': form,
        'task': task
    })
