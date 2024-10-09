from .models import ThemeSettings, ModeSettings

def theme_settings(request):
    if request.user.is_authenticated:
        try:
            settings = ThemeSettings.objects.get(user=request.user)
        except ThemeSettings.DoesNotExist:
            settings = None
        return {'theme_settings': settings}
    return {}

def mode_settings(request):
    if request.user.is_authenticated:
        try:
            settings = ModeSettings.objects.get(user=request.user)
        except ModeSettings.DoesNotExist:
            settings = None
        return {'mode_settings': settings}
    return {}