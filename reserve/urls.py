from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework import routers

from .views import *
from . import views


router_chat = SimpleRouter()
router_chat.register(r'', ChatViewset, basename='Chat')


router_message = SimpleRouter()
router_message.register(r'', MessageViewset, basename='Message')

salon_router = SimpleRouter()
salon_router.register(r'salons', SalonViewSet,  basename='salons')

barber_profile_router = SimpleRouter()
customer_profile_router = SimpleRouter()
barber_profile_router.register(r'barbers/profiles', BarberProfileViewSet, basename='barber-profiles')
customer_profile_router.register(r'customers/profiles', CustomerProfileViewSet, basename='customer-profiles')

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='Login'),
    path('logout/', LogoutAPIView.as_view(), name='Logout'),
    path('CustomerSignup/', CustomerSignupAPIView.as_view(), name='CustomerSignup'),
    path('BarberSignup/', BarberSignupAPIView.as_view(), name='BarberSignup'),
    path('password_reset_request/', PasswordResetRequestAPIView.as_view(), name='password_reset_request'),
    path('password_reset/<str:token>/', PasswordResetAPIView.as_view(), name='password_reset'),
    path('token_validation/', TokenValidation.as_view(), name='token_validation'),
    path('', include(salon_router.urls)),
    path('', include(barber_profile_router.urls)),
    path('', include(customer_profile_router.urls)),
    path('HomeUp',LandingUPViewSet.as_view(),name='LandingUP'),
    path('HomeMid',LandingMidViewSet.as_view(),name='LandingMid'),
    path('HomeDown',LandingDownViewSet.as_view(),name='LandingDown'),
    path('LandingGifs',LandingGifsViewSet.as_view(),name='LandingGifs'),
    path('barbers/<int:barber_id>/reviews/', BarberReviewsAPIView.as_view(), name='barber-reviews'),
    path('salons/<int:salon_id>/reviews/', SalonReviewsAPIView.as_view(), name='salon-reviews'),
    path('reviews/', ReviewDetailAPIView.as_view(), name = 'all-review-detail'),
    path('reviews/<int:review_id>/responses/', ResponseAPIView.as_view(), name='response-list-create'),
    path('reviews/responses/<int:pk>/', SingleResponseAPIView.as_view(), name = 'response-detail'),
    path('chats/', include(router_chat.urls)),
    path('chats/<int:chat_id>/messages/', include(router_message.urls)),
    path('reserve/<int:barber_id>/day/<str:day>/', BlockedAndAppointmentTimes.as_view(), name='blocked_and_appointment_times'),
    path('appointments/', AppointmentCreateAPIView.as_view(), name='appointment-create'),
    path('C_orders/<int:Customer_id>',OrdersOfEachCustumerAPIView.as_view(),name='Customer_Orders'),
    path('B_orders/<int:barber_id>',OrdersOfEachBarberAPIView.as_view(),name='Barber_Orders'),
    path('barbers/<int:barber_id>/stats/', BarberStatsView.as_view(), name='barber-stats'),
]