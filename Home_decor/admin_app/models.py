from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(models.Model):
    email = models.EmailField(unique=True,null=False)
    username = models.CharField(max_length=100)

    USERNAME_FIELD = "email"
    REQUIRED_FIELD = ['username']

    def __str__(self):
        return self.username
