from taskFlow.models import Profile

def user_profile(request):
    """Profil zalogowanego użytkownika dostępny w każdym szablonie."""
    if not request.user.is_authenticated:
        return {"user_profile": None}
    profile, _created = Profile.objects.get_or_create(user=request.user)
    return {"user_profile": profile}
