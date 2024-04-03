from django.urls import path
from .views import LoginAPIView
from .views import CustomerSignupAPIView,BarberSignupAPIView
from .views import PasswordResetAPIView,PasswordResetRequestAPIView

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='Login'),
    path('CustomerSignup/', CustomerSignupAPIView.as_view(), name='CustomerSignup'),
    path('BarberSignup/', BarberSignupAPIView.as_view(), name='BarberSignup'),
    path('password_reset_request/', PasswordResetRequestAPIView.as_view(), name='password_reset_request'),
    path('password_reset/<str:token>/', PasswordResetAPIView.as_view(), name='password_reset'),
]