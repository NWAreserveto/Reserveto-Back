from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer
from .serializers import BarberSignupSerializer,CustomerSignupSerializer
from django.shortcuts import get_object_or_404
from .serializers import PasswordResetSerializer
from .models import PasswordReset
import uuid
from .models import *
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import authenticate


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
                elif is_customer:
                    role = "customer"
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'role': role
                })
            else:
                return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate token
        token = str(uuid.uuid4())
        password_reset = PasswordReset.objects.create(user=user, token=token, expires_at=timezone.now() + timezone.timedelta(hours=1))
        
        # Send email
        send_password_reset_email(user, token)

        return Response({'message': 'Password reset email sent successfully'}, status=status.HTTP_200_OK)


class PasswordResetAPIView(APIView):
    def post(self, request, token):
        password_reset = PasswordReset.objects.filter(token=token, expires_at__gte=timezone.now()).first()
        if not password_reset:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            user = password_reset.user
            user.set_password(serializer.validated_data['password'])
            user.save()
            password_reset.delete()
            return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

# class EmailVerificationAPIView(APIView):
#     def get(self, request, user_id):
#         user = get_object_or_404(User, id=user_id)
#         if not user.email_verified:
#             user.email_verified = True
#             user.save()
#             return Response({'detail': 'Email verified successfully.'}, status=status.HTTP_200_OK)
#         return Response({'detail': 'Email is already verified.'}, status=status.HTTP_400_BAD_REQUEST)

def generate_token(user):
    token = uuid.uuid4()
    password_reset = PasswordReset(user=user,token=token,expires_at=timezone.now() + timezone.timedelta(hours=1))
    password_reset.save()
    return token

def send_password_reset_email(user, token):
    subject = 'Password Reset'
    message = f'Hello {user.username},\n\nPlease click the link below to reset your password:\n\n{settings.BASE_URL}/reset_password/{token}'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email],fail_silently=False)



# def send_verification_email(user):
#     subject = 'Email Verification'
#     message = f'Hello {user.username},\n\nPlease click the link below to verify your email:\n\n{settings.BASE_URL}/verify-email/{user.id}'
#     send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

