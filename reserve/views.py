from rest_framework import status, viewsets, mixins, generics, filters
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer
from .serializers import *
from .serializers import *
from collections import defaultdict
from .models import PasswordReset
import uuid
import os
# from .tasks import reply_chat
from .models import *
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import authenticate
from .permissions import *
from rest_framework.permissions import IsAuthenticated
# import openai


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data = request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                is_barber = Barber.objects.filter(user=user).exists()
                is_customer = Customer.objects.filter(user=user).exists()
                if is_barber:
                    role = "barber"
                    tmp = Barber.objects.get(user=user)
                    obj_serializer = BarberSerializer(tmp)
                    obj_data = obj_serializer.data

                elif is_customer:
                    role = "customer"
                    tmp = Customer.objects.get(user=user)
                    obj_serializer = CustomerSerializer(tmp)
                    obj_data = obj_serializer.data

                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'role': role,
                    role.capitalize(): obj_data
                },
                status=status.HTTP_200_OK)
            else:
                return Response({'خطا': 'مشخصات نامعتبر است '}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class LogoutAPIView(APIView):
    def post(self, request):
        permission_classes = [IsAuthenticated]
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'پیغام': 'خروج موفقیت آمیز'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'خطا': 'خروج ناموفق'}, status=status.HTTP_400_BAD_REQUEST)
    
class BarberSignupAPIView(APIView):
    def post(self, request):
        serializer = BarberSignupSerializer(data=request.data)
        if serializer.is_valid():
            barber = serializer.save()
            refresh = RefreshToken.for_user(barber)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'barber': BarberSignupSerializer(barber).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CustomerSignupAPIView(APIView):
    def post(self, request):
        serializer = CustomerSignupSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            refresh = RefreshToken.for_user(customer.user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'customer': CustomerSignupSerializer(customer).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'خطا': 'کاربری با این ایمیل وجود ندارد'}, status=status.HTTP_400_BAD_REQUEST)
        
        token = str(uuid.uuid4())
        password_reset = PasswordReset.objects.create(user=user, token=token, expires_at=timezone.now() + timezone.timedelta(hours=12))
        
        send_password_reset_email(user, token)

        return Response({'پیغام': 'ایمیل بازیابی رمز عبور با موفقیت ارسال شد'}, status=status.HTTP_200_OK)


class PasswordResetAPIView(APIView):
    def post(self, request, token):
        password_reset = PasswordReset.objects.filter(token=token, expires_at__gte=timezone.now()).first()

        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            user = password_reset.user
            user.set_password(serializer.validated_data['password'])
            user.save()
            password_reset.delete()
            return Response({'پیغام': 'رمز عبور با موفقیت بازیابی شد'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class TokenValidation(APIView):
    def post(self,request) :
        token = request.data.get('token')
        password_reset = PasswordReset.objects.filter(token=token, expires_at__gte=timezone.now()).first()
        if not password_reset:
            return Response({'خطا': ' توکن نامعتبر یا منقضی شده است'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'پیغام': ' توکن معتبر است'}, status=status.HTTP_202_ACCEPTED)


def generate_token(user):
    token = uuid.uuid4()
    password_reset = PasswordReset(user=user,token=token,expires_at=timezone.now() + timezone.timedelta(hours=1))
    password_reset.save()
    return token

def send_password_reset_email(user, token):
    subject = 'Password Reset'
    message = f'Hello {user.username},\n\nPlease click the link below to reset your password:\n\n{settings.BASE_URL}/password_reset/{token}/'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email],fail_silently=False)



class BarberAdminMixin:
    permission_classes = [IsBarberAdminSalonWithJWT]

class UserOwnerMixin:
    permission_classes = [IsUserOwnerWithJWT]

class SalonViewSet(BarberAdminMixin, mixins.ListModelMixin,
                   mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Salon.objects.all()
    serializer_class = SalonSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            permission_classes = [IsBarberAdminSalonWithJWTForUpdate]
        elif self.action in ['list', 'retrieve']:  
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsBarberAdminSalonWithJWT]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return super().get_queryset()

    def perform_update(self, serializer):
        # Save the instance to get the updated data
        instance = serializer.save()

        # Update the list of barbers associated with the salon
        barbers_data = self.request.data.get('barber', [])
        instance.barber.set(barbers_data)

    def perform_partial_update(self, serializer):
        # Save the instance to get the updated data
        instance = serializer.save()

        # Update the list of barbers associated with the salon
        barbers_data = self.request.data.get('barber', [])
        instance.barber.set(barbers_data)

class BarberProfileViewSet(viewsets.ModelViewSet):
    queryset = Barber.objects.all()
    serializer_class = BarberSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'user__username']
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsBarberOwnerWithJWT]
        elif self.action in ['list', 'retrieve']:  
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super(BarberProfileViewSet, self).get_permissions()

    def perform_create(self, serializer):
        serializer.save(barber=self.request.user.barber)

    def partial_update(self, request, *args, **kwargs):
        user_data = self.request.data.get('user')
        print("Updating barber profile for user:", self.request.user.username) 

        if user_data:
            print("User data received for update:", user_data)  
            user_serializer = UserSerializer(instance=self.request.user, data=user_data, partial=True)

            is_valid = user_serializer.is_valid()
            print("User serializer validation:", is_valid)  
            if is_valid:
                user_serializer.save()
            else:
                print("User serializer errors:", user_serializer.errors)  
        barber = self.get_object()

        barber_serializer = BarberSignupSerializer(instance=barber, data=request.data, partial=True)

        if not barber_serializer.is_valid():
            return Response(barber_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        barber_serializer.save()
        return Response(barber_serializer.data)

    def perform_update(self, serializer):
            user_data = self.request.data.get('user')
            if user_data:
                user_serializer = UserSerializer(instance=self.request.user, data=user_data, partial=True)
                if user_serializer.is_valid(raise_exception=True):
                    user_serializer.save()

            return super().perform_update(serializer)

class CustomerProfileViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsCustomerOwnerWithJWT]
        else:
            self.permission_classes = [IsAuthenticated]
        return super(CustomerProfileViewSet, self).get_permissions()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)

    def perform_update(self, serializer):
        serializer.save(customer=self.request.user.customer)

class LandingUPViewSet(generics.ListAPIView):
    queryset = LandingUP.objects.all()
    serializer_class = LandingUPSerializer

class LandingMidViewSet(generics.ListAPIView):
    queryset = LandingMid.objects.all()
    serializer_class = LandingMidSerializer

class LandingDownViewSet(generics.ListAPIView):
    queryset = LandingDown.objects.all()
    serializer_class = LandingDownSerializer


class LandingGifsViewSet(generics.ListAPIView):
    queryset = LandingGifs.objects.all()
    serializer_class = LandingGifsSerializer

class BarberReviewsAPIView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        barber_id = self.kwargs['barber_id']
        return Review.objects.filter(recipient_barber_id=barber_id)

    def perform_create(self, serializer):
        barber_id = self.kwargs['barber_id']
        barber = Barber.objects.get(pk=barber_id)
        reviewer = self.request.user.customer
        serializer.save(reviewer=reviewer, recipient_barber=barber)

class SalonReviewsAPIView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return []

    def get_queryset(self):
        salon_id = self.kwargs['salon_id']
        return Review.objects.filter(salon_id=salon_id)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

class ReviewDetailAPIView(generics.ListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class ResponseAPIView(generics.ListCreateAPIView):
    queryset = ResponseMessage.objects.all()
    serializer_class = ResponseSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [CanRespondToReview()]
        elif self.request.method == 'GET':
            return [IsAuthenticated()]
        return []

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        return ResponseMessage.objects.filter(review_id=review_id, responder=self.request.user.barber)

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = Review.objects.get(pk=review_id)
        serializer.save(review=review, responder=self.request.user.barber)


class SingleResponseAPIView(generics.RetrieveUpdateAPIView):
    queryset = ResponseMessage.objects.all()
    serializer_class = ResponseSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        elif self.request.method == 'PUT' or self.request.method == 'PATCH':
            return [CanRespondToReview()]
        return super().get_permissions()
    




class ChatViewset(DestroyModelMixin, UpdateModelMixin, GenericViewSet):

    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user).order_by('-updated_at')

    def get_serializer_class(self):
        return ChatSerializer

    def format_queryset(self, queryset):
        dates = defaultdict(list)
        for chat in queryset:
            date = str(chat.created_at.date())
            dates[date].append({
                'id': chat.id,
                'title': chat.title
            })
        return [{'date': key, 'chats': value} for key, value in dates.items()]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return Response(self.format_queryset(queryset=queryset))

    def create(self, request, *args, **kwargs):
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.validated_data['text'][:20]
        chat = Chat.objects.create(user=request.user, title=title)
        text = serializer.validated_data['text']
        message = Message.objects.create(chat=chat, text=text)
        reply = reply_chat(chat.id, text)
        message.reply=reply
        message.save()
        return Response({
            'chat_id': chat.id,
            'reply': reply,
            'message_id': message.id,
        })
    def delete(self, request, *args, **kwargs):
        self.get_queryset().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class MessageViewset(mixins.ListModelMixin, GenericViewSet):
    serializer_class = MessageSerializer

    def get_chat(self):
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, id=chat_id)
        if chat.user != self.request.user:
            raise PermissionDenied()
        return chat

    def get_queryset(self):
        return self.get_chat().messages.all().order_by('-created_at')

    def create(self, request, *args, **kwargs):
        chat = self.get_chat()
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        text = serializer.validated_data['text']
        mes = Message.objects.create(chat=chat, text=text)
        mes.reply = reply_chat(chat.id, text)
        mes.save()

        return Response({
            'message_id':mes.id,
            'reply': mes.reply,
        })

class BlockedAndAppointmentTimes(generics.ListAPIView):
    queryset =BlockedTimesOfBarber.objects.all()
    serializer_class = AppointmentSerializer
    
    def get_queryset_blocked_times(self, barber_id, day):
        return BlockedTimesOfBarber.objects.filter(barber_id=barber_id, day=day)

    def get_queryset_appointment_times(self, barber_id, day):
        return Appointment.objects.filter(barber_id=barber_id, day=day)

    def get(self, request, *args, **kwargs):
        barber_id = self.kwargs.get('barber_id')
        day = self.kwargs.get('day')

        queryset_blocked_times = self.get_queryset_blocked_times(barber_id, day)
        queryset_appointment_times = self.get_queryset_appointment_times(barber_id, day)

        blocked_times_data = BlockedTimesOfBarberSerializer(queryset_blocked_times, many=True).data
        appointment_times_data = Appointment_Serializer(queryset_appointment_times, many=True).data

        response_data = {
            'blocked_times': blocked_times_data,
            'appointment_times': appointment_times_data
        }

        return Response(response_data)
from rest_framework.decorators import api_view

class AppointmentCreateAPIView(generics.CreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)