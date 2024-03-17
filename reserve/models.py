from django.contrib.auth.models import User
from django.db import models
import uuid
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now() + timezone.timedelta(hours=1))
    class Meta:
        app_label = 'reserve'

class Salon(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class Barber(models.Model):
    first_name = models.CharField(max_length = 256)
    last_name = models.CharField(max_length = 256)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    salons = models.ManyToManyField(Salon, related_name='barbers')  
    experience_years = models.IntegerField()
    services_offered = models.TextField()  # A simple text field to list services; consider a ManyToMany relationship for more complexity
    created_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)  # Admin flag for barbers
    def __str__(self):
        return self.user.username


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length = 256)
    last_name = models.CharField(max_length = 256)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    preferences = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username




# class User(AbstractUser):
#     email_verified = models.BooleanField(default=False)
#     class Meta:
#         app_label = 'reserve'