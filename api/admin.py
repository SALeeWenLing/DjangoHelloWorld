from django.contrib import admin
from .models import Task, DevelopmentTag, Sprint, ThemeSettings, ModeSettings
from simple_history.admin import SimpleHistoryAdmin

class TaskAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    list_display = ('task_name', 'status', 'sprint')
    list_editable = ('status', 'sprint')

class SprintAdmin(admin.ModelAdmin):
    list_display = ('sprint_name', 'status', 'activated', 'start_date', 'end_date')
    list_editable = ('status', 'activated', 'start_date', 'end_date')

class ThemeSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme')
    search_fields = ('user__username', 'theme')

class ModeSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'mode')
    search_fields = ('user__username', 'mode')

admin.site.register(Task, TaskAdmin)
admin.site.register(DevelopmentTag)
admin.site.register(Sprint, SprintAdmin)
admin.site.register(ThemeSettings, ThemeSettingsAdmin)
admin.site.register(ModeSettings, ModeSettingsAdmin)
