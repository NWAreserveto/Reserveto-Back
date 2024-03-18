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

    def __str__(self):
        return f"Username :{self.user.username} + Created at : {self.created} + Expires at : {self.expires_at}"


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    duration = models.DurationField()
    salon = models.ForeignKey('Salon', on_delete=models.CASCADE, related_name='services')
    barbers = models.ManyToManyField('Barber', related_name='services', blank=True)

    def __str__(self):
        return self.name

class Salon(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    profile_picture = models.ImageField(upload_to='salon_profiles/', blank=True, null=True)


    def __str__(self):
        return self.name

class Barber(models.Model):
    first_name = models.CharField(max_length = 256)
    last_name = models.CharField(max_length = 256)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    salons = models.ManyToManyField(Salon, related_name='barbers')  
    experience_years = models.IntegerField()
    services_offered = models.ManyToManyField(Service)
    created_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)  # Admin flag for barbers
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='barber_profiles/', blank=True, null=True)
    def __str__(self):
        return self.user.username


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length = 256)
    last_name = models.CharField(max_length = 256)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    preferences = models.TextField()
    profile_picture = models.ImageField(upload_to='customer_profiles/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username



    
class Review(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='reviews')
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='reviews')
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.user.username} - {self.barber.user.username} - {self.rating}"
    
class Appointment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    services = models.ManyToManyField(Service, related_name='appointments')
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='bookings')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username} - {', '.join([service.name for service in self.services.all()])} - {self.barber.user.username} - {self.start_time}"    

class Gallery(models.Model):
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='gallery_images', null=True, blank=True)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='gallery_images', null=True, blank=True)
    image = models.ImageField(upload_to='gallery/')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# class User(AbstractUser):
#     email_verified = models.BooleanField(default=False)
#     class Meta:
#         app_label = 'reserve'