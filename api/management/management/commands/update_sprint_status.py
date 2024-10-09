# from django.core.management.base import BaseCommand
# from django.utils import timezone
# from main.models import Sprint
# from datetime import date  # FOR TESTING PURPOSES


# class Command(BaseCommand):
#     help = 'Update sprint statuses based on the current date'

#     def handle(self, *args, **kwargs):
#         today = date(2024, 9, 24)  # FOR TESTING PURPOSES
#         # Command:
#         '''
#         python3 manage.py update_sprint_status
#         python3 manage.py runserver  
#         '''

#         # today = timezone.now().date()
#         sprints = Sprint.objects.all().order_by('start_date')
#         active_sprint_exists = False
        
#         for sprint in sprints:
#             if sprint.end_date < today:
#                 sprint.status = 'Inactive'
#             elif sprint.start_date <= today <= sprint.end_date:
#                 if not active_sprint_exists:
#                     sprint.status = 'Active'
#                     active_sprint_exists = True
#                 else:
#                     sprint.status = 'Upcoming'
#             else:
#                 sprint.status = 'Upcoming'
#             sprint.save()
        
#         self.stdout.write(self.style.SUCCESS('Successfully updated sprint statuses'))


from django.core.management.base import BaseCommand
from main.utils import update_sprint_statuses
from datetime import date  # FOR TESTING PURPOSES
from django.utils import timezone

class Command(BaseCommand):
    help = 'Update sprint statuses based on the current date'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        update_sprint_statuses(today)
        self.stdout.write(self.style.SUCCESS('Successfully updated sprint statuses'))