from django import forms
from .models import Task, ProgressTracking

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        widgets = {
            'proposed_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'expected_completion_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'details': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 设置初始日期值
        if not self.instance.pk:
            self.initial['proposed_date'] = timezone.now().strftime('%Y-%m-%dT%H:%M')

        # 设置必填字段
        self.fields['name'].required = True
        self.fields['proposer'].required = True
        self.fields['project'].required = True
        
        # 确保 task_id 字段存在
        if 'task_id' in self.fields:
            # 对于已存在的任务，禁用task_id字段
            if self.instance and self.instance.pk:
                self.fields['task_id'].disabled = True
            # 对于新任务，隐藏task_id字段，因为它会自动生成
            else:
                self.fields['task_id'].widget = forms.HiddenInput()
                self.fields['task_id'].required = False

class ProgressTrackingForm(forms.ModelForm):
    class Meta:
        model = ProgressTracking
        fields = ['progress_description']
        widgets = {
            'progress_description': forms.Textarea(attrs={'rows': 5}),
        }