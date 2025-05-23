from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.urls import reverse
from .models import Task, ProgressTracking
from .forms import TaskForm, ProgressTrackingForm

class TaskListView(ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 处理筛选条件
        proposer = self.request.GET.get('proposer')
        project = self.request.GET.get('project')
        parent_task = self.request.GET.get('parent_task')
        priority = self.request.GET.get('priority')
        status = self.request.GET.get('status')
        
        if proposer:
            queryset = queryset.filter(proposer=proposer)
        if project:
            queryset = queryset.filter(project=project)
        if parent_task:
            queryset = queryset.filter(parent_task=parent_task)
        if priority:
            queryset = queryset.filter(priority=priority)
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset.order_by('-proposed_date')

def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            # 自动生成task_id的逻辑现在在模型的save方法中
            task = form.save()
            return redirect(reverse('tasks:task_update', kwargs={'pk': task.pk}))
    else:
        # 为新表单设置初始值
        initial_data = {'proposed_date': timezone.now(),}
        form = TaskForm(initial=initial_data)
    
    return render(request, 'tasks/task_create.html', {'form': form})

def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect(reverse('tasks:task_update', kwargs={'pk': task.pk}))
    else:
        form = TaskForm(instance=task)
    
    # 获取该任务的所有进度跟踪
    progress_list = task.progress_trackings.all().order_by('-update_date')
    
    return render(request, 'tasks/task_update.html', {
        'form': form,
        'task': task,
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
            return redirect(reverse('tasks:task_update', kwargs={'pk': task.pk}))
    else:
        form = ProgressTrackingForm()
    
    return render(request, 'tasks/progress_create.html', {
        'form': form,
        'task': task
    })
