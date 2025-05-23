from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.core.exceptions import ValidationError

class Task(models.Model):
    # 任务状态选择
    STATUS_CHOICES = [
        ('PENDING', '待开始'),
        ('IN_PROGRESS', '进行中'),
        ('ON_HOLD', '已暂缓'),
        ('CLOSED', '已关闭'),
        ('CANCELLED', '已取消'),
    ]
    
    # 优先级选择
    PRIORITY_CHOICES = [
        ('P0', 'P0 - 最高优先级'),
        ('P1', 'P1 - 高优先级'),
        ('P2', 'P2 - 中优先级'),
        ('P3', 'P3 - 低优先级'),
    ]
    
    # 任务编号 - REQ+4位数字流水码
    task_id = models.CharField(
        '任务编号',
        max_length=7,  # TAS+4位数字
        unique=True,
        blank=True,  # 允许在表单中为空，因为我们会自动生成
        editable=False, # 在admin中不可编辑
        validators=[MinLengthValidator(7)]
    )
    
    # 任务派发部分
    name = models.CharField('任务名称', max_length=50)
    proposer = models.CharField('提出者', max_length=5)
    proposed_date = models.DateTimeField('提出日期', auto_now_add=True)
    details = models.TextField('任务详情')
    #expected_completion_date = models.DateField('期望完成日期')
    expected_completion_date = models.DateField('期望完成日期', null=True, blank=False)
    
    # 任务协作部分
    executor = models.CharField('执行人', max_length=5)
    project = models.CharField('所属项目', max_length=50)  # 关联项目主数据，实际项目中建议使用ForeignKey
    related_object_code = models.CharField(
        '所属需求/风险编码', 
        max_length=7,
        help_text='前三个字符为"REQ"或"RIS"'
    )
    related_name = models.CharField('所属需求/风险名称', max_length=50, blank=True)
    participants = models.CharField('参与人', max_length=50, help_text='多个参与人用逗号分隔')
    parent_task = models.CharField('父任务', max_length=7, blank=True, null=True)
    
    # 任务跟踪部分
    status = models.CharField(
        '任务状态',
        max_length=11,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    priority = models.CharField(
        '优先级',
        max_length=2,
        choices=PRIORITY_CHOICES,
        default='P2'
    )
    deliverable_location = models.CharField('交付物存放位置', max_length=255, blank=True)
    
    class Meta:
        verbose_name = '任务'
        verbose_name_plural = '任务清单'
        ordering = ['-proposed_date']
    
    def __str__(self):
        return f"{self.task_id} - {self.name}"
    
    def clean(self):
        # 验证期望完成日期不小于提出日期
        if self.expected_completion_date and self.proposed_date:
            if self.expected_completion_date < self.proposed_date.date():
                raise ValidationError({'expected_completion_date': '期望完成日期不能小于提出日期'})
        
        # 验证关联编码格式
        if self.related_object_code and not self.related_object_code[:3] in ['REQ', 'RIS']:
            raise ValidationError({'related_object_code': '关联编码必须以REQ或RIS开头'})
    
    def save(self, *args, **kwargs):
        # 自动生成任务编号（如果新建）
        if not self.task_id:
            last_task = Task.objects.order_by('-id').first()
            last_id = int(last_task.task_id[3:]) if last_task else 0
            self.task_id = f"TAS{str(last_id + 1).zfill(4)}"
        
        super().save(*args, **kwargs)

class ProgressTracking(models.Model):
    # 关联类型选项
    RELATED_TYPE_CHOICES = [
        ('REQ', '需求'),
        ('TASK', '任务'),
        ('RISK', '风险'),
        ('PROJECT', '项目'),
    ]

    # 进度编号 - 8位流水码
    tracking_id = models.CharField(
        '进度编号',
        max_length=8,
        unique=True,
        editable=False
    )
    
    # 基本信息
    update_date = models.DateField('更新日期', auto_now=True)
    progress_description = models.TextField('进度说明', max_length=500)
    
    # 关联对象
    related_object_code = models.CharField(
        '所属需求/任务/风险/项目编码',
        max_length=7,
        help_text='根据所在页面自动填入'
    )
    
    related_type = models.CharField(
        '关联类型',
        max_length=7,
        choices=RELATED_TYPE_CHOICES,
        default='TASK'
    )

    # 关联任务（可选）
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='progress_tracks',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = '进度跟踪'
        verbose_name_plural = '进度跟踪'
        ordering = ['-update_date']
    
    def __str__(self):
        return f"{self.tracking_id} - {self.update_date}"
    
    def clean(self):
        # 验证关联编码格式
        if self.related_object_code and not self.related_object_code[:3] in ['REQ','TAS', 'RIS','PRO']:
            raise ValidationError({'related_object_code': '关联编码必须以REQ、TAS、RIS或PRO开头'})
        '''if self.related_type == 'REQ' and not self.related_object_code.startswith('REQ'):
            raise ValidationError({'related_object_code': '需求编码应以REQ开头'})
        elif self.related_type == 'RISK' and not self.related_object_code.startswith('RIS'):
            raise ValidationError({'related_object_code': '风险编码应以RIS开头'})
        elif self.related_type == 'TASK' and not self.related_object_code.startswith('REQ'):
            raise ValidationError({'related_object_code': '任务编码应以REQ开头'})'''

    def save(self, *args, **kwargs):
        # 自动生成进度编号（如果新建）
        if not self.tracking_id:
            last_tracking = ProgressTracking.objects.order_by('-id').first()
            last_id = int(last_tracking.tracking_id) if last_tracking else 0
            self.tracking_id = str(last_id + 1).zfill(8)
        
        super().save(*args, **kwargs)