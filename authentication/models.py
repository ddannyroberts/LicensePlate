"""
Authentication models - Migrated from Flask User model
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    Migrated from Flask SQLAlchemy User model

    Original Flask model:
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(150), unique=True, nullable=False)
        password_hash = db.Column(db.String(256), nullable=False)
        is_admin = db.Column(db.Boolean, default=False)
    """
    is_admin = models.BooleanField(
        default=False,
        help_text='Designates whether the user can access admin features.'
    )

    class Meta:
        db_table = 'auth_user'  # Keep consistent with Django's default
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

    @property
    def is_admin_user(self):
        """Check if user is admin or staff"""
        return self.is_admin or self.is_staff or self.is_superuser