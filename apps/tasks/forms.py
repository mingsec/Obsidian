from django import forms
from django.utils import timezone
from .models import Task, ProgressTracking

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'name', 'proposer', 'proposed_date', 'details','expected_completion_date',
            'executor', 'project', 'related_code','related_name', 'parent_task', 'participants', 'status', 'priority'
        ]
        widgets = {
            'proposed_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%mm-%dd'),
            'expected_completion_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%mm-%dd'),
            'details': forms.Textarea(attrs={'rows': 3}),
            'participants': forms.TextInput(attrs={'placeholder': '多个参与人用逗号分隔'}),
        }
        '''
        labels = {
            'name': '任务名称*',
            'proposer': '提出人*',
            'project': '所属项目*',
        }
        '''
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 设置初始日期值
        if not self.instance.pk:
            self.initial['proposed_date'] = timezone.now().strftime('%Y-%mm-%dd')


class TaskUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'executor', 'project', 'related_code',
            'related_name', 'parent_task', 'participants', 'status', 'priority'
        ]
        widgets = {
            'participants': forms.TextInput(attrs={'placeholder': '多个参与人用逗号分隔'}),
        }


class ProgressTrackingForm(forms.ModelForm):
    class Meta:
        model = ProgressTracking
        fields = ['progress_description', 'task']
        widgets = {'progress_description': forms.Textarea(attrs={'rows': 5}),}
        # labels = {'progress_description': '进度说明*'}