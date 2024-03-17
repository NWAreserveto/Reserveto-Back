from django.contrib import admin
from .models import *

admin.site.register(PasswordReset)
admin.site.register(Barber)
admin.site.register(Customer)
admin.site.register(Salon)