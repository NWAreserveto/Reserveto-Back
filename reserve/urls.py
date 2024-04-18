from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import *



salon_router = SimpleRouter()
salon_router.register(r'salons', SalonViewSet,  basename='salons')

barber_profile_router = SimpleRouter()
customer_profile_router = SimpleRouter()
barber_profile_router.register(r'barbers/profiles', BarberProfileViewSet, basename='barber-profiles')
customer_profile_router.register(r'customers/profiles', CustomerProfileViewSet, basename='customer-profiles')

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='Login'),
    path('CustomerSignup/', CustomerSignupAPIView.as_view(), name='CustomerSignup'),
    path('BarberSignup/', BarberSignupAPIView.as_view(), name='BarberSignup'),
    path('password_reset_request/', PasswordResetRequestAPIView.as_view(), name='password_reset_request'),
    path('password_reset/<str:token>/', PasswordResetAPIView.as_view(), name='password_reset'),
    path('', include(salon_router.urls)),
    path('', include(barber_profile_router.urls)),
    path('', include(customer_profile_router.urls)),
]