from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework import routers

from .views import *
from . import views


router_chat = SimpleRouter()
router_chat.register(r'', ChatViewset, basename='Chat')

router_notification = SimpleRouter()
router_notification.register(r'notifications', NotificationViewSet, basename = 'Notification')

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
    path('barbers/<int:id>/barber-hours/', BarberHoursUpdateView.as_view(), name='barber_hours_update'),
    path('barbers/stats/', BarberStatsView.as_view(), name='barber-stats'),
    path('barbers/<int:barber_id>/gallery/', GalleryListView.as_view(), name='gallery-list'),
    path('barbers/<int:barber_id>/gallery/upload/', GalleryCreateView.as_view(), name='gallery-upload'),
    path('', include(router_notification.urls)),
    path('notifications/<int:notification_id>/confirm_appointment/', NotificationViewSet.as_view({'post': 'confirm_appointment'}), name='confirm_appointment'),
    path('notifications/<int:notification_id>/reject_appointment/', NotificationViewSet.as_view({'post': 'reject_appointment'}), name='reject_appointment'),
    path('cart/', CartCreateAPIView.as_view(), name='cart-create'),
    path('cart/list/', CartListAPIView.as_view(), name='cart-list'), 
    path('cart/<int:cart_id>/confirm/', ConfirmCartView.as_view(), name='confirm-cart'),
    path('cart/<int:cart_id>/reject/', RejectCartView.as_view(), name='reject-cart'),
    path('appointment/<int:appointment_id>/confirm/', CustomerOrderConfirm.as_view(), name='confirm-appointment'),
    path('appointment/<int:appointment_id>/reject/', CustomerOrderReject.as_view(), name='reject-appointment'),
    path('allservices/', AllServicesAPIView.as_view(), name='all-services'),
    path('customers/<int:customer_id>/bookmarks/', BookmarksAPIView.as_view(),name='bookmarks'),
    path('barbers/<int:salon_id>/requests/', CreateRequestView.as_view(), name='create-request'),
    path('barbers/admin/requests/confirmation/<int:pk>/', ApproveRejectRequestView.as_view(), name='approve-reject-request'),
    path('barbers/requests/', BarberRequestsView.as_view(), name='barber-requests'),
    path('salon/<int:salon_id>/requests/', SalonRequestsView.as_view(), name='salon-requests'),
    path('blocked-times/', BlockedTimeCreateView.as_view(), name='blocked_times_create'),

]