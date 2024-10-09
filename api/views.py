from datetime import datetime, timezone

from django.db.transaction import commit
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from .utils import update_sprint_statuses
from .forms import CreateNewList, SprintForm, ThemeSettingsForm, RegisterForm, AdminUserChangeForm, StaffUserChangeForm, ModeSettingsForm
from .models import Task, Sprint, ThemeSettings, ModeSettings
from .forms import CreateNewList, SprintForm, ThemeSettingsForm, RegisterForm, AdminUserChangeForm, StaffUserChangeForm, \
    TimeLogForm
from .models import Task, Sprint, ThemeSettings, TimeLog
from django.views import View
from django.db.models import Case, When, IntegerField, Value
import json
from django.urls import reverse
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin




# Create your views here.

@login_required
def theme_settings(request):
    try:
        theme_settings = ThemeSettings.objects.get(user=request.user)
    except ThemeSettings.DoesNotExist:
        theme_settings = ThemeSettings(user=request.user)

    try:
        mode_settings = ModeSettings.objects.get(user=request.user)
    except ModeSettings.DoesNotExist:
        mode_settings = ModeSettings(user=request.user)

    if request.method == 'POST':
        theme_form = ThemeSettingsForm(request.POST, instance=theme_settings)
        mode_form = ModeSettingsForm(request.POST, instance=mode_settings)

        if theme_form.is_valid() and mode_form.is_valid():
            theme_form.save()
            mode_form.save()
            return redirect('theme_settings')
    else:
        theme_form = ThemeSettingsForm(instance=theme_settings)
        mode_form = ModeSettingsForm(instance=mode_settings)

    return render(request, 'forms/theme_settings.html', {
        'form': theme_form,
        'mode_form': mode_form,
    })

# THEME AND MODE IMPLEMENTED SEPARATELY, DELETE WHEN LIGHT/DARK MODES ARE 100% IMPLEMENTED

# @login_required
# def theme_settings(request):
#     try:
#         settings = ThemeSettings.objects.get(user=request.user)
#     except ThemeSettings.DoesNotExist:
#         settings = ThemeSettings(user=request.user)

#     if request.method == 'POST':
#         form = ThemeSettingsForm(request.POST, instance=settings)
#         if form.is_valid():
#             form.save()
#             return redirect('theme_settings')
#     else:
#         form = ThemeSettingsForm(instance=settings)

#     return render(request, 'forms/theme_settings.html', {'form': form})

# @login_required
# def mode_settings(request):
#     try:
#         settings = ModeSettings.objects.get(user=request.user)
#     except ModeSettings.DoesNotExist:
#         settings = ModeSettings(user=request.user)

#     if request.method == 'POST':
#         form = ModeSettingsForm(request.POST, instance=settings)
#         if form.is_valid():
#             form.save()
#             return redirect('theme_settings')
#     else:
#         form = ModeSettingsForm(instance=settings)

#     return render(request, 'forms/theme_settings.html', {'form': form})


def home(request):
    return render(request, "main/home.html", {})


# < ---------- Login / Registration Views ---------- >

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)  # Use auth_login to avoid conflict with the view name
            return redirect('home')  # Redirect to a success page
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

@login_required
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("team_dashboard")
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def edit_user_admin(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = AdminUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User details updated successfully!')  # Success message
            return redirect('team_dashboard')  # Redirect to the team dashboard after saving
    else:
        # Goes to the update page
        form = AdminUserChangeForm(instance=user)
    return render(request, 'forms/edit_user_admin.html', {'form': form})


@login_required
def edit_user_staff(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = StaffUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User details updated successfully!')  # Success message
            return redirect('team_dashboard')  # Redirect to the team dashboard after saving
        else:
            messages.error(request, 'Please give the correct original password')  # Success message
    else:
        form = StaffUserChangeForm(instance=user)
    return render(request, 'forms/edit_user_staff.html', {'form': form})


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy('team_dashboard')  # Redirect to the team dashboard after deletion
    template_name = 'users/user_confirm_delete.html'  # Template for confirmation

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        Task.objects.filter(assignee=self.object).update(assignee=None)
        self.object.delete()
        return JsonResponse({'success': 'User deleted successfully.'})


# < ---------- Team Dashboard Views ---------- >

@login_required
def team_dashboard(request):
    if request.user.is_superuser or request.user.is_staff:
        users = User.objects.all()
    else:
        users = User.objects.filter(id = request.user.id)    
    return render(request, 'main/team_dashboard.html', {'users': users})

# @login_required
# def create_user(request):
#     if request.method == 'POST':
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'User created successfully.')
#             return redirect(reverse('team_dashboard'))
#     else:
#         form = RegisterForm()
#     return render(request, 'main/team_dashboard.html', {'form': form})


# < ---------- Sprint Views ---------- >

@login_required
def sprint_dashboard(request):
    sort_by = request.GET.get('sort_by', 'start_date')  # Default sorting by start_date
    if sort_by not in ['sprint_name', 'start_date', 'end_date']:
        sort_by = 'start_date'  # Fallback to default if invalid sort_by value is provided

    status_filter = request.GET.getlist('status')
    sprints = Sprint.objects.all().order_by(sort_by)

    if status_filter:
        sprints = sprints.filter(status__in=status_filter)

    selected_date = request.GET.get('selected_date')
    if selected_date:
        current_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        current_date = timezone.now().date()
    return render(request, 'main/sprint_dashboard.html', {'sprints': sprints, 'current_date': current_date})

@login_required
def toggle_sprint_date(request):
    if request.method == 'POST':
        selected_date = request.POST.get('selected_date')
        if selected_date:
            today = datetime.strptime(selected_date, '%Y-%m-%d').date()
        else:
            today = timezone.now().date()

        # Call the function to update sprint statuses
        update_sprint_statuses(today)

        # Redirect to the sprint dashboard with the selected date as a query parameter
        return redirect(f'/sprint_dashboard/?selected_date={selected_date}')
    else:
        return render(request, 'main/toggle_date.html')

@login_required
def create_sprint(request):
    if request.method == 'POST':
        form = SprintForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('sprint_dashboard'))
    else:
        form = SprintForm()
    return render(request, 'main/sprint_dashboard.html', {'form': form})

@csrf_exempt
@login_required
def update_sprint_status(request, sprint_id):
    if request.method == 'POST' and request.user.is_superuser:
        print("Received POST request")
        data = json.loads(request.body)
        new_status = data.get('status')
        end_sprint = data.get('endSprint', False)
        try:
            sprint = Sprint.objects.get(id=sprint_id)
            print(f"Updating sprint {sprint_id} to status {new_status}")
            sprint.status = new_status

            # Set activated to True if the new status is Active
            if new_status == 'Active':
                sprint.activated = True

            sprint.save()

            if end_sprint:
                # Update tasks that are "not started" or "in progress" to unassign from the sprint
                tasks_to_update = Task.objects.filter(sprint_id=sprint_id, status__in=['Not Started', 'In Progress'])
                print(f"Tasks to update: {tasks_to_update}")
                tasks_to_update.update(sprint=None)

            return JsonResponse({'success': True})
        except Sprint.DoesNotExist:
            print("Sprint not found")
            return JsonResponse({'success': False, 'error': 'Sprint not found'})
    print("Invalid request")
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def edit_sprint(request, sprint_id):
    sprint = get_object_or_404(Sprint, id=sprint_id)
    if request.method == 'POST':
        form = SprintForm(request.POST, instance=sprint)
        if form.is_valid():
            form.save()
            return redirect('sprint_dashboard')  # Redirect to the sprint dashboard after saving
    else:
        form = SprintForm(instance=sprint)
    return render(request, 'forms/edit_sprint.html', {'form': form})

@login_required
def inactive_sprint(request, sprint_id):
    sprint = get_object_or_404(Sprint, id=sprint_id, status='Inactive')

    filter_by = request.GET.get('filter_by', '')  # Comma-separated list of tags
    sort_by = request.GET.get('sort_by', 'status')  # Default sort by status

    if sort_by == 'priority_high':
        order_by = Case(
            When(priority='Urgent', then=Value(1)),
            When(priority='Important', then=Value(2)),
            When(priority='Medium', then=Value(3)),
            When(priority='Low', then=Value(4)),
            output_field=IntegerField()
        )
    elif sort_by == 'priority_low':
        order_by = Case(
            When(priority='Low', then=Value(1)),
            When(priority='Medium', then=Value(2)),
            When(priority='Important', then=Value(3)),
            When(priority='Urgent', then=Value(4)),
            output_field=IntegerField()
        )
    elif sort_by == 'newest_date':
        order_by = '-created_at'
    elif sort_by == 'oldest_date':
        order_by = 'created_at'
    else:
        order_by = 'status'

    # Filter tasks assigned to the active sprint and apply sorting
    # Fetch tasks and sort them into columns based on status
    tasks = Task.objects.all().order_by(order_by)

    # Apply filtering by tags if provided
    if filter_by:
        tags = filter_by.split(',')
        tasks = tasks.filter(development_tag__name__in=tags).distinct()

    context = {
        'tasks': tasks,
        'sprint': sprint,
    }

    return render(request, 'main/inactive_sprint.html', context)


@login_required
def active_sprint(request, sprint_id):
    sprint = get_object_or_404(Sprint, id=sprint_id, status='Active')

    filter_by = request.GET.get('filter_by', '')  # Comma-separated list of tags
    sort_by = request.GET.get('sort_by', 'status')  # Default sort by status

    if sort_by == 'priority_high':
        order_by = Case(
            When(priority='Urgent', then=Value(1)),
            When(priority='Important', then=Value(2)),
            When(priority='Medium', then=Value(3)),
            When(priority='Low', then=Value(4)),
            output_field=IntegerField()
        )
    elif sort_by == 'priority_low':
        order_by = Case(
            When(priority='Low', then=Value(1)),
            When(priority='Medium', then=Value(2)),
            When(priority='Important', then=Value(3)),
            When(priority='Urgent', then=Value(4)),
            output_field=IntegerField()
        )
    elif sort_by == 'newest_date':
        order_by = '-created_at'
    elif sort_by == 'oldest_date':
        order_by = 'created_at'
    else:
        order_by = 'status'

    # Filter tasks assigned to the active sprint and apply sorting
    tasks = Task.objects.filter(sprint=sprint).order_by(order_by)

    # Apply filtering by tags if provided
    if filter_by:
        tags = filter_by.split(',')
        tasks = tasks.filter(development_tag__name__in=tags).distinct()

    context = {
        'tasks': tasks,
        'sprint': sprint,
    }

    return render(request, 'main/active_sprint.html', context)

@login_required
def completed_sprint(request, sprint_id):
    sprint = get_object_or_404(Sprint, id=sprint_id, status='Completed')
    
    filter_by = request.GET.get('filter_by', '')  # Comma-separated list of tags
    sort_by = request.GET.get('sort_by', 'status')  # Default sort by status
    
    if sort_by == 'priority_high':
        order_by = Case(
            When(priority='Urgent', then=Value(1)),
            When(priority='Important', then=Value(2)),
            When(priority='Medium', then=Value(3)),
            When(priority='Low', then=Value(4)),
            output_field=IntegerField()
        )
    elif sort_by == 'priority_low':
        order_by = Case(
            When(priority='Low', then=Value(1)),
            When(priority='Medium', then=Value(2)),
            When(priority='Important', then=Value(3)),
            When(priority='Urgent', then=Value(4)),
            output_field=IntegerField()
        )
    elif sort_by == 'newest_date':
        order_by = '-created_at'
    elif sort_by == 'oldest_date':
        order_by = 'created_at'
    else:
        order_by = 'status'

    # Filter tasks assigned to the active sprint and apply sorting
    tasks = Task.objects.filter(sprint=sprint, status='Completed').order_by(order_by)

    # Apply filtering by tags if provided
    if filter_by:
        tags = filter_by.split(',')
        tasks = tasks.filter(development_tag__name__in=tags).distinct()

    context = {
        'tasks': tasks,
        'sprint': sprint,
    }

    return render(request, 'main/completed_sprint.html', context)

@login_required
def delete_sprint(request, sprint_id):
    sprint = get_object_or_404(Sprint, id=sprint_id)

    if sprint.status != 'Inactive':
        return JsonResponse({'error': 'Only inactive sprints can be deleted.'}, status=400)

    # Reassign all tasks linked to this sprint back to the product backlog
    tasks = Task.objects.filter(sprint=sprint)
    tasks.update(sprint=None)  # Set the sprint to None, indicating it's back in the product backlog

    # Now, delete the sprint
    sprint.delete()

    return JsonResponse({'success': 'Sprint deleted successfully.'})


# < ---------- Product Backlog Views ---------- >

@login_required
def product_backlog(request):
    filter_by = request.GET.get('filter_by', '')  # Comma-separated list of tags
    sort_by = request.GET.get('sort_by', 'status')  # Default sort by status

    if sort_by == 'priority_high':
        order_by = Case(
            When(priority='Urgent', then=Value(1)),
            When(priority='Important', then=Value(2)),
            When(priority='Medium', then=Value(3)),
            When(priority='Low', then=Value(4)),
            output_field=IntegerField()
        )
    elif sort_by == 'priority_low':
        order_by = Case(
            When(priority='Low', then=Value(1)),
            When(priority='Medium', then=Value(2)),
            When(priority='Important', then=Value(3)),
            When(priority='Urgent', then=Value(4)),
            output_field=IntegerField()
        )
    elif sort_by == 'newest_date':
        order_by = '-created_at'
    elif sort_by == 'oldest_date':
        order_by = 'created_at'
    else:
        order_by = 'status'

    # Fetch tasks and sort them into columns based on status
    tasks = Task.objects.all().order_by(order_by)

    # Apply filtering by tags if provided
    if filter_by:
        tags = filter_by.split(',')
        tasks = tasks.filter(development_tag__name__in=tags).distinct()

    context = {
        'tasks': tasks,
    }

    return render(request, "main/product_backlog.html", context)


# < ---------- Task Views ---------- >

@login_required
def create_task(request):
    if request.method == "POST":
        form = CreateNewList(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            form.save()
            form.save_m2m()
            return redirect("product_backlog")
    else:
        form = CreateNewList()
    template_name = "forms/create_task.html"
    context = {
        "form": form,
        "action": "create",
        "isCreate": True
    }
    return render(request, template_name, context)


# @login_required
# def create_task(request, task_id=None):
#     if task_id:
#         task = get_object_or_404(Task, id=task_id)
#     else:
#         task = None

#     if request.method == 'POST':
#         if request.user.is_superuser or request.user.is_staff:
#             form = CreateNewList(request.POST, instance=task)
#         else:
#             form = CreateNewList(request.POST, instance=task)
#             if form.is_valid():
#                 task = form.save(commit=False)
#                 task.status = form.cleaned_data['status']
#                 task.save()
#                 # form.save_m2m()  # Save the many-to-many relationships
#                 return redirect('product_backlog')
#     else:
#         form = CreateNewList(instance=task)

#     return render(request, 'forms/create_task.html', {'form': form, 'action': 'update' if task else 'create'})





@login_required
def update_task(request, f_id):
    obj = get_object_or_404(Task, id=f_id)
    form = CreateNewList(instance=obj)
    timelog_form = TimeLogForm(user=request.user, task=obj)
    if request.method == "POST":
        form = CreateNewList(request.POST, instance=obj)
        if form.is_valid():
            print("VALID")
            form.save()
            # Create an instance of the TimeLog model
            timelog = TimeLog.objects.create(user=request.user, task=obj, time_spent=0, date=timezone.now())
            timelog.user = request.user
            timelog.task = obj
            print("timelog")
            print(timelog.date)
            print(timelog.task)
            print(timelog)
            timelog.save()


            timelog_form = TimeLogForm(request.POST, instance=timelog, task=obj, user=request.user)
            timelog_form.save()

            return redirect(request.GET.get('next', 'product_backlog'))
    template_name = "forms/create_task.html"
    context = {
        "form": form,
        "action": "update",
        "task": obj,
        "timelog_form": timelog_form
    }
    return render(request, template_name, context)




def viewHistory(request, f_id):
    task = get_object_or_404(Task, id=f_id)
    history = task.history.all()  # Fetch all history records
    # Get date and user only
    history_data = [
        {
            "history_date": timezone.localtime(object.history_date).strftime('%B %d, %Y %I:%M %p'),  
            "history_user": object.history_user.username if object.history_user else "None"
        }
        for object in history
    ]
    return JsonResponse(history_data, safe=False)


@login_required
def delete_task(request, id):
    if request.method == 'DELETE':
        task = get_object_or_404(Task, id=id)
        task.delete()
        return JsonResponse({'message': 'Task deleted successfully.'})
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def get_task(request, task_id):
    try:
        task = get_object_or_404(Task, id=task_id)
        task_data = {
            'id': task.id,
            'name': task.task_name,
            'description': task.description,
            'priority': task.priority,
            'sprint_name': task.sprint.sprint_name if task.sprint else None,
        }
        return JsonResponse({'success': True, 'task': task_data})
    except Task.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found'})




def update_task_without_frontend(request, task_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            print("Received data:", data)  # Debugging line
            task = Task.objects.get(id=task_id)
            # get the sprint object
            if data['task']['sprint_name'] == None:
                task.sprint = None
            else:
                sprint = Sprint.objects.get(sprint_name=data['task']['sprint_name'])
                task.sprint = sprint

            print("Updated sprint name:", task.sprint)  # Debugging line
            task.save()

            task_data = {
                'id': task.id,
                'name': task.task_name,
                'description': task.description,
                'priority': task.priority,
                'sprint_name': task.sprint,
            }
            print(f"Task sprint after update: {task.sprint}")
            print("Task data to return:", task_data )# Debugging line
            return JsonResponse({'success': True, 'task': task_data})
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'})
        except Sprint.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Sprint not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

