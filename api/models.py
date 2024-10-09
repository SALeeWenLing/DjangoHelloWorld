from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from simple_history.models import HistoricalRecords

# Create your models here.

MODE_CHOICES = [
    ('dark', 'Dark'),
    ('light', 'Light'),
]

class ModeSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mode = models.CharField(max_length=12, choices=MODE_CHOICES, default='light')

    def __str__(self):
        return f"{self.user.username}'s Mode Settings"
    
    class Meta:
        verbose_name = "Mode setting"
        verbose_name_plural = "Mode settings"

THEME_CHOICES = [
    ('deadpool', 'Deadpool'),
    ('bubblegum', 'Bubblegum'),
    ('ocean', 'Ocean'),
    ('nature', 'Nature'),
]

class ThemeSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme = models.CharField(max_length=12, choices=THEME_CHOICES, default='default')

    def __str__(self):
        return f"{self.user.username}'s Theme Settings"

    class Meta:
        verbose_name = "Theme setting"
        verbose_name_plural = "Theme settings"
        

class Sprint(models.Model):
    STATUS_CHOICES = [
        ('Inactive', 'Inactive'),
        ('Active', 'Active'),
        ('Completed', 'Completed'),
    ]

    sprint_name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Inactive')
    activated = models.BooleanField(default=False) 

    def __str__(self):
        return self.sprint_name

class Task(models.Model):
    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('Important', 'Important'),
        ('Urgent', 'Urgent'),
    ]

    TASK_STAGES = [
        ('Project Planning', 'Project Planning'),
        ('Development', 'Development' ),
        ('Testing','Testing' ),
        ('Integration', 'Integration'),
    ]

    TASK_TYPES = [
        ('Bug', 'Bug'),
        ('User Story', 'User Story')
    ]

    task_name = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=9, choices=PRIORITY_CHOICES, default='Medium')
    # assignee = models.ForeignKey(User, on_delete=models.CASCADE)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    story_point = models.IntegerField()
    development_tag = models.ManyToManyField('DevelopmentTag')
    done = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Started')
    task_stage = models.CharField(max_length=16, choices=TASK_STAGES, default='Project Planning')
    task_type = models.CharField(max_length=16, choices=TASK_TYPES, default='User Story')
    created_at = models.DateTimeField(default=timezone.now)
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE, null=True, blank=True, default=None)
    history = HistoricalRecords()

    def __str__(self):
        return self.task_name
    

class DevelopmentTag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class TimeLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    time_spent = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.time_spent} hours on {self.date} for {self.task.task_name}"

