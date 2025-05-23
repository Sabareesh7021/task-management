from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    parent_id = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True) 
    class Meta:
        db_table = "users"


    
