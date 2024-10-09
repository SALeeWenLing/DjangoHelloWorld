

# utils.py
from datetime import date
from django.utils import timezone
from api.models import Sprint

def update_sprint_statuses(today=None):
    if today is None:
        today = timezone.now().date()
    
    sprints = Sprint.objects.all().order_by('start_date')
    active_sprint_exists = False
    
    for sprint in sprints:
        if sprint.status == 'Completed':
            continue

        if sprint.start_date <= today <= sprint.end_date:
            if not active_sprint_exists:
                sprint.status = 'Active'
                sprint.activated = True
                active_sprint_exists = True
            else:
                sprint.status = 'Inactive'
        elif sprint.activated == True:
            if sprint.end_date < today:
                sprint.status = 'Completed'
        else:
            sprint.status = 'Inactive'
        sprint.save()