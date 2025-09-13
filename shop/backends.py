from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class UsernameOrEmailBackend(ModelBackend):
    """
    Custom auth backend: allow login with either username OR email.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            # Match username OR email (case-insensitive)
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # Edge case: duplicate email somehow (shouldn’t happen if email is unique=True)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
