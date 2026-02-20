from django.shortcuts import render


def settings_view(request):
    # TODO: Load user profile data from request.user.userprofile
    # For now, pass placeholder context
    return render(request, 'settings_page/settings.html')
