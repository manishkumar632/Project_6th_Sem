from django.db import models
from django.contrib.auth.models import AbstractUser
from decouple import config

class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    bio = models.TextField(null=True, blank=True)
    profileImage = models.URLField(max_length=500, blank=True, null=True, default=config('DEFAULT_PROFILE_IMAGE'))
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=False, null=False, default='M')

    # Use email as the primary identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email