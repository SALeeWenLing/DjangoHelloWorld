from django.urls import path, include
from django.contrib import admin
from .views import *


urlpatterns = [
    
    path('accounts/', include('django.contrib.auth.urls')),

    path("", home, name="home"),
    path("home/", home, name="home"),
    path('register/', register, name='register'),
    path("create_task/", create_task, name="create"),

    # Settings Views
    path('theme_settings/', theme_settings, name='theme_settings'),

    # Team Views
    path('team_dashboard/', team_dashboard, name='team_dashboard'),
    path('edit_user_admin/<int:user_id>/', edit_user_admin, name='edit_user_admin'),
    path('edit_user_staff/<int:user_id>/', edit_user_staff, name='edit_user_staff'),
    path('delete_user/<int:pk>/', UserDeleteView.as_view(), name='delete_user'),

    # Sprint Views
    path('sprint_dashboard/', sprint_dashboard, name='sprint_dashboard'),
    path('toggle_sprint_date/', toggle_sprint_date, name='toggle_sprint_date'),
    path('create_sprint/', create_sprint, name='create_sprint'),
    path('update_sprint_status/<int:sprint_id>/', update_sprint_status, name='update_sprint_status'),
    path('edit_sprint/<int:sprint_id>/', edit_sprint, name='edit_sprint'),
    path('delete_sprint/<int:sprint_id>/', delete_sprint, name='delete_sprint'), 
    path('active_sprint/<int:sprint_id>/', active_sprint, name='active_sprint'),
    path('inactive_sprint/<int:sprint_id>/', inactive_sprint, name='inactive_sprint'),
    path('completed_sprint/<int:sprint_id>/', completed_sprint, name='completed_sprint'),

    # Product Backlog Views
    path('product_backlog/', product_backlog, name='product_backlog'),
    path('product_backlog/<int:id>/', product_backlog, name='product_backlog'),
    path('update_task/<int:f_id>/', update_task, name='update_task'),
    path('task/delete/<int:id>/', delete_task, name='delete_task'),
    path('task/viewHistory/<int:f_id>/', viewHistory, name='viewHistory'),
    path('task/<int:task_id>/', get_task, name='get_task'), # New path for getting a single task

    path('task/update/<int:task_id>/', update_task_without_frontend, name='update_task_without_frontend'),  # New path for updating a single task


] 