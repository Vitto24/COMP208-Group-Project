from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def settings_view(request):
    # TODO: Load user profile data from request.user.userprofile
    # For now, pass placeholder context
    return render(request, 'settings_page/settings.html')
