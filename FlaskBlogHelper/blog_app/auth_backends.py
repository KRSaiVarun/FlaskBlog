from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.exceptions import MultipleObjectsReturned
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EmailOrUsernameModelBackend(ModelBackend):
    """Authentication backend that allows users to log in using either username or email.

    Features:
    - Case-insensitive matching for both username and email
    - Proper handling of multiple user matches
    - Timing attack protection
    - Comprehensive logging
    - Integration with Django's get_user_model()
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """Authenticate a user based on username/email and password.

        Returns the User instance on success or None on failure.
        """
        user_model = get_user_model()

        if username is None or password is None:
            logger.debug("Authentication attempted with missing username or password")
            return None

        # Clean the input
        username = username.strip()

        user = None
        try:
            # Case-insensitive lookup for username or email
            user = user_model._default_manager.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except user_model.DoesNotExist:
            # User not found - run password hasher for timing attack protection
            logger.debug(f"Authentication failed: No user found with username/email '{username}'")
            # instantiate a user and set password to run the hasher
            user_model().set_password(password)
            return None
        except MultipleObjectsReturned:
            # Handle multiple users with same email (shouldn't happen with unique constraint)
            # But we'll handle it defensively by trying exact username match first
            logger.warning(f"Multiple users found for username/email '{username}'")

            try:
                user = user_model._default_manager.get(username__iexact=username)
            except user_model.DoesNotExist:
                # If multiple users have the same email, return the first active one
                users = (
                    user_model._default_manager.filter(email__iexact=username, is_active=True)
                    .order_by('date_joined')
                )

                if users.exists():
                    user = users.first()
                    logger.warning(
                        f"Selected user '{getattr(user, 'username', None)}' from multiple matches for email '{username}'"
                    )
                else:
                    user_model().set_password(password)
                    return None

        # Verify password and check if user can authenticate
        if user and user.check_password(password) and self.user_can_authenticate(user):
            logger.info(f"User '{user.username}' authenticated successfully")
            return user

        logger.debug(
            f"Authentication failed for user '{getattr(user, 'username', None)}' - invalid password or inactive account"
        )
        return None

    def get_user(self, user_id):
        """Get a user by their primary key.

        Returns the User object if found and able to authenticate, otherwise None.
        """
        user_model = get_user_model()

        try:
            user = user_model._default_manager.get(pk=user_id)
            return user if self.user_can_authenticate(user) else None
        except (user_model.DoesNotExist, ValueError, TypeError):
            logger.debug(f"User with ID '{user_id}' not found or invalid ID")
            return None

    def user_can_authenticate(self, user):
        """Check if the user can authenticate.

        Override the parent method if you need custom logic.
        """
        is_active = getattr(user, 'is_active', None)

        # Add any additional authentication checks here
        # For example, check if user's email is verified, account is not locked, etc.

        return is_active or is_active is None
