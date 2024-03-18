from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return value
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Password and Confirm Password do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)


class BarberSignupSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Barber
        fields = ['id','user', 'first_name', 'last_name', 'phone_number','created_at']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.save()
            if 'experience_years' in validated_data:
                experience_years = validated_data.pop('experience_years')
            else:
                experience_years = 0  

            barber = Barber.objects.create(user=user, experience_years=experience_years, **validated_data)
            salons_data = self.initial_data.get('salons')
            if salons_data:
                for salon_id in salons_data:
                    salon = Salon.objects.get(pk=salon_id)
                    barber.salons.add(salon)
            return barber
    
class CustomerSignupSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.save()
            customer = Customer.objects.create(user=user, **validated_data)
            return customer
    
class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data
