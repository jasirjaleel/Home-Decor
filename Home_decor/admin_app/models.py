from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

# Create your models here.

# class User(models.Model):
#     email = models.EmailField(unique=True,null=False)
#     username = models.CharField(max_length=100)

#     USERNAME_FIELD = "email"
#     REQUIRED_FIELD = ['username']

#     def __str__(self):
#         return self.username
    

class Category(models.Model):

    category_name = models.CharField(max_length=50, unique=True)
    slug          = models.SlugField(max_length=100, unique=True)
    description   = models.TextField(max_length=255, blank=True)
    cat_image     = models.ImageField(upload_to='media/categories', blank=True)
    
    class Meta:
        verbose_name        = 'category'
        verbose_name_plural = 'categories'

    def __str__(self) :
        return self.category_name
    

