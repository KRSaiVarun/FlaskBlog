from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authentication backend that allows users to log in using either username or email
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to find a user matching this username or email
            user = User.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            # Run the default password hasher a single time to reduce timing attacks
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # If multiple users are found (e.g., same email used for different usernames)
            # try to get the exact username match
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None