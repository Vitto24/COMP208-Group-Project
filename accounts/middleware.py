from django.shortcuts import redirect
from django.urls import reverse

# paths a half-registered student is still allowed to visit
SETUP_ALLOWED = (
    'accounts:select_modules',
    'accounts:randomise_modules',
    'accounts:logout',
    'accounts:password_reset',
    'accounts:password_reset_done',
    'accounts:password_reset_confirm',
    'accounts:password_reset_complete',
)


class RegistrationCompleteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed = set()
        for name in SETUP_ALLOWED:
            try:
                self.allowed.add(reverse(name))
            except Exception:
                pass

    def __call__(self, request):
        user = getattr(request, 'user', None)

        if user and user.is_authenticated and not user.is_staff:
            profile = getattr(user, 'userprofile', None)
            if profile and not profile.registration_complete:
                if not any(request.path.startswith(p) for p in self.allowed):
                    return redirect('accounts:select_modules')

        return self.get_response(request)
