from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.core.exceptions import ValidationError

class Task(models.Model):
    # 项目名称选项
    PROJECT_CHOICES = [
        ('PRJ0001', '建设FSSC(1期)'),
        ('PRJ0002', '建设PMS'),
        ('PRJ0003', '建设闲置资产管理系统'),
        ('PRJ0004', '香港公司切换SAP系统'),
        ('PRJ0005', '建设关务系统'),
        ('PRJ0006', '上线贸易订单转自动生产工单功能'),
        ('PRJ0007', '金属报表优化(3期)'),
        ('PRJ0008', '财务数据可视化'),
        ('PRJ0009', '建设动电回收物联网平台'),
        ('PRJ0010', '数字化规划硬仗经营分析子项目'),
        ('PRJ0011', '建设FSSC(2期)'),
        ('PRJ0012', '建设税务信息化管理平台'),
        ('PRJ0013', '需求管理'),
        ('PRJ0014', 'SAP及周边系统运维'),
        ('PRJ0015', 'BFS运维'),
        ('PRJ0016', 'BPC运维'),
        ('PRJ0017', 'OA运维'),
        ('PRJ0018', '财务信息化体系建设'),
        ('PRJ0019', '财经流程导入EBPM'),
        ('PRJ0020', '财经分授权调整'),
        ('PRJ0021', '其他'),
    ]
    
    # 任务状态选择
    STATUS_CHOICES = [
        ('PENDING', '待开始'),
        ('IN_PROGRESS', '进行中'),
        ('ON_HOLD', '已暂缓'),
        ('CLOSED', '已关闭'),
        ('CANCELLED', '已取消'),
    ]
    
    # 优先级选择
        # P0:立即启动，资源优先保障，限时完成
        # P1:排入当月计划，确保资源投入
        # P2:根据资源情况安排，可纳入后续月份工作
        # P3:暂缓实施
    PRIORITY_CHOICES = [
        ('P0', 'P0 - 资源优先保障，限时完成'),
        ('P1', 'P1 - 排入当月计划'),
        ('P2', 'P2 - 纳入后续月份'),
        ('P3', 'P3 - 暂缓实施'),
    ]
    
    # 任务编号 - REQ+4位数字流水码
    task_id = models.CharField(
        '任务编号',
        max_length=7,  # TAS+4位数字
        unique=True,
        blank=True,  # 允许在表单中为空，因为我们会自动生成
        validators=[MinLengthValidator(7)]
    )
    
    # 基本信息
    name = models.CharField('任务名称', max_length=30, null=False, blank=False)
    proposer = models.CharField('提出者', max_length=5, null=False, blank=False)
    proposed_date = models.DateTimeField('提出日期', default=timezone.now, null=False, blank=False)
    details = models.TextField('任务详情', blank=True, null=True)
    expected_completion_date = models.DateField('期望完成日期', null=False, blank=False)
    
    # 协作信息
    executor = models.CharField('执行人', max_length=5, null=False, blank=False, db_index=True)
    project = models.CharField('所属项目', max_length=7, choices=PROJECT_CHOICES, null=False, blank=False, db_index=True)
    related_code = models.CharField('所属需求/风险编码', max_length=7, blank=True, null=True, help_text='前三个字符为"REQ"或"RIS"')
    related_name = models.CharField('所属需求/风险名称', max_length=50, blank=True, null=True)
    parent_task = models.CharField('父任务', max_length=7, blank=True, null=True)
    participants = models.CharField('参与人', max_length=50, blank=True, null=True, help_text='多个参与人用逗号分隔')
    status = models.CharField('任务状态', max_length=11, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    priority = models.CharField('优先级', max_length=2, choices=PRIORITY_CHOICES, default='P2', db_index=True)
    last_updated = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        verbose_name = '任务'
        verbose_name_plural = '任务清单'
        ordering = ['-proposed_date']
    
    def __str__(self):
        return f"{self.task_id} - {self.name}"
    
    def clean(self):
        # 验证期望完成日期不小于提出日期
        if self.expected_completion_date and self.proposed_date:
            raise ValidationError({'expected_completion_date': '期望完成日期不能小于提出日期'})
    
    def save(self, *args, **kwargs):
        # 自动生成任务编号（如果新建）
        if not self.task_id:
            last_task = Task.objects.order_by('-id').first()
            last_id = int(last_task.task_id[3:]) if last_task else 0
            self.task_id = f"TAS{str(last_id + 1).zfill(4)}"   
        super().save(*args, **kwargs)

class ProgressTracking(models.Model):
    tracking_id = models.CharField('进度编号', max_length=8, unique=True, editable=False)
    update_date = models.DateField('更新日期', auto_now=True)
    progress_description = models.TextField('进度说明', max_length=500, null=False, blank=False)
    related_object_code = models.CharField('关联需求/任务/风险项目编码', max_length=7, blank=True, null=True)    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='progress_trackings',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = '进度跟踪'
        verbose_name_plural = '进度跟踪'
        ordering = ['-update_date']
    
    def __str__(self):
        return f"{self.tracking_id} - {self.update_date}"
    
    def save(self, *args, **kwargs):
        # 自动生成进度编号
        if not self.tracking_id:
            last_tracking = ProgressTracking.objects.order_by('-id').first()
            last_id = int(last_tracking.tracking_id) if last_tracking else 0
            self.tracking_id = str(last_id + 1).zfill(8)    
        super().save(*args, **kwargs)