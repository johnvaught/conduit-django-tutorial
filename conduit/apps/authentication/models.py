from rest_framework_simplejwt.tokens import RefreshToken
import jwt

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db import models


class UserManager(BaseUserManager):
    """
    Django requires that custom users define their own Manager class. By
    inheriting from `BaseUserManager`, we get a lot of the same code used by
    Django to create a `User`.

    All we have to do is override the `create_user` function which we will use
    to create `User` objects.
    """

    def create_user(self, handle, email, password=None):
        """Create and return a `User` with an email, username and password."""
        if handle is None:
            raise TypeError('Users must have a handle.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(handle=handle, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, handle, email, password):
        """
        Create and return a `User` with superuser (admin) permissions.
        """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(handle, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    handle = models.CharField(db_index=True, max_length=15, unique=True)
    email = models.EmailField(db_index=True, unique=True)

    # These are implemented in AbstractBaseUser
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # More fields required by Django when specifying a custom user model.

    # The `USERNAME_FIELD` property tells us which field we will use to log in.
    # In this case we want it to be the email field.
    USERNAME_FIELD = 'handle'
    REQUIRED_FIELDS = ['email']

    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()

    def __str__(self):
        return self.handle

    @property
    def refresh_token(self):
        """
        Allows us to get a user's token by calling `user.token` instead of
        `user.generate_jwt_tokens().

        The `@property` decorator above makes this possible. `refresh_token` is called
        a "dynamic property".
        """
        return self.generate_jwt_tokens()['refresh']

    @property
    def access_token(self):
        return self.generate_jwt_tokens()['access']

    def get_full_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically this would be the user's first and last name. Since we do
        not store the user's real name, we return their handle instead.
        """
        return self.handle

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first name. Since we do not store
        the user's real name, we return their username instead.
        """
        return self.handle

    def generate_jwt_tokens(self):
        """
        Generates a JSON Web Token that stores this user's ID and has an expiry
        date set to 60 days into the future.
        """
        refresh = RefreshToken.for_user(self)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
