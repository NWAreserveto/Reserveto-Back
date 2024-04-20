from rest_framework import status, viewsets, mixins, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer
from .serializers import *
from django.shortcuts import get_object_or_404
from .serializers import *
from .models import PasswordReset
# from .models import Landing
import uuid
from .models import *
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import authenticate
from .permissions import *
from rest_framework.permissions import IsAuthenticated


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
                return Response({'خطا': 'مشخصات نامعتبر است '}, status=status.HTTP_401_UNAUTHORIZED)
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
            return Response({'خطا': 'کاربری با این ایمیل وجود ندارد'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate token
        token = str(uuid.uuid4())
        password_reset = PasswordReset.objects.create(user=user, token=token, expires_at=timezone.now() + timezone.timedelta(hours=1))
        
        # Send email
        send_password_reset_email(user, token)

        return Response({'پیغام': 'ایمیل بازیابی رمز عبور با موفقیت ارسال شد'}, status=status.HTTP_200_OK)


class PasswordResetAPIView(APIView):
    def post(self, request, token):
        password_reset = PasswordReset.objects.filter(token=token, expires_at__gte=timezone.now()).first()
        if not password_reset:
            return Response({'خطا': ' توکن نامعتبر یا منقضی شده است'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            user = password_reset.user
            user.set_password(serializer.validated_data['password'])
            user.save()
            password_reset.delete()
            return Response({'پیغام': 'رمز عبور با موفقیت بازیابی شد'}, status=status.HTTP_200_OK)
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
    message = f'Hello {user.username},\n\nPlease click the link below to reset your password:\n\n{settings.BASE_URL}/password_reset/{token}/'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email],fail_silently=False)



# def send_verification_email(user):
#     subject = 'Email Verification'
#     message = f'Hello {user.username},\n\nPlease click the link below to verify your email:\n\n{settings.BASE_URL}/verify-email/{user.id}'
#     send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])


# Base ViewSets or Mixins
class BarberAdminMixin:
    permission_classes = [IsBarberAdminSalonWithJWT]

class UserOwnerMixin:
    permission_classes = [IsUserOwnerWithJWT]

# Salon ViewSet
class SalonViewSet(BarberAdminMixin, mixins.ListModelMixin,
                   mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Salon.objects.all()
    serializer_class = SalonSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            permission_classes = [IsBarberAdminSalonWithJWTForUpdate]
        else:
            permission_classes = [IsBarberAdminSalonWithJWT]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return super().get_queryset()

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class BarberProfileViewSet(viewsets.ModelViewSet):
    queryset = Barber.objects.all()
    serializer_class = BarberSignupSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsBarberOwnerWithJWT]
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
    serializer_class = CustomerSignupSerializer

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

class LandingViewSet(viewsets.ModelViewSet):
    def get_page(self):
        landing = Landing.objects.all()
        serializer = LandingSerializer(landing)
        return Response(serializer.data)