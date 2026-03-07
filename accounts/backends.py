from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailBackend(ModelBackend):
    """Let users log in with their email instead of a username."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Django's login form sends the email in the 'username' field
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None

        # Check the password and make sure the account is active
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
