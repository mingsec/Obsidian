from django import forms
from django.utils import timezone
from bootstrap_datepicker_plus import DatePickerInput
from .models import Task, ProgressTracking

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'name', 'proposer', 'proposed_date', 'details','expected_completion_date',
            'executor', 'project', 'related_code','related_name', 'parent_task', 'participants', 'status', 'priority'
        ]
        widgets = {
            'proposed_date': forms.DatePickerInput(format='%Y-%mm-%dd'),
            'expected_completion_date': forms.DatePickerInput(format='%Y-%mm-%dd'),
            'details': forms.Textarea(attrs={'rows': 3}),
            'participants': forms.TextInput(attrs={'placeholder': '多个参与人用逗号分隔'}),
        }
        help_texts = {
            'related_code': '前三个字符为"REQ"或"RIS"',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 设置初始日期值
        if not self.instance.pk:
            self.initial['proposed_date'] = timezone.now().strftime('%Y-%mm-%dd')

    def clean(self):
        cleaned_data = super().clean()
        
        # 验证日期
        proposed_date = cleaned_data.get('proposed_date')
        expected_date = cleaned_data.get('expected_completion_date')
        
        if proposed_date and expected_date:
            if expected_date < proposed_date:
                self.add_error('expected_completion_date', '期望完成日期不能小于提出日期')

        return cleaned_data

        
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
    update_date = forms.DateField(
        widget=DatePickerInput(format='%Y-%mm-%dd'),
        initial=timezone.now().date()
    )

    class Meta:
        model = ProgressTracking
        fields = ['progress_description', 'task']
        widgets = {'progress_description': forms.Textarea(attrs={'rows': 5}),}