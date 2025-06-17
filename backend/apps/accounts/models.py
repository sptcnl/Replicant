from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    GENDER_CHOICE = (
            ('M', 'Man'),
            ('W', 'Woman'),
            ('O', 'Other'),
        )
    username = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICE, blank=True, null=True)

    def __str__(self):
        return self.username