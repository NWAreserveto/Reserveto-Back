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
    
    def validate_username(self, value):
        # If this is an update operation and the username hasn't changed, skip the uniqueness check
        if self.instance and self.instance.username == value:
            return value

        # Check for uniqueness
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists .")
        return value
    
    def validate(self, data):
        if 'password' in data and 'confirm_password' in data:
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError({"password": "Password and Confirm Password do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        user = User.objects.create_user(**validated_data)
        return user
    

def update(self, instance, validated_data):
    new_username = validated_data.get('username')
    if new_username and new_username != instance.username:
        if User.objects.filter(username=new_username).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        instance.username = new_username

    instance.email = validated_data.get('email', instance.email)

    new_password = validated_data.get('password')
    if new_password:
        instance.set_password(new_password)

    instance.save()
    return instance
        
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)


class BarberSignupSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Barber
        fields = ['id','user', 'first_name', 'last_name', 'phone_number','created_at']


        def update(self, instance, validated_data):
            # Extract the user data from the validated data
            user_data = validated_data.pop('user', None)

            # Update the User instance if user data is provided
            if user_data:
                user = instance.user
                user_serializer = UserSerializer(user, data=user_data, partial=True)
                if user_serializer.is_valid(raise_exception=True):
                    user = user_serializer.save()

            # Update the Barber instance
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            return instance

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
    

class BarberSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    profile_picture = serializers.ImageField(required=False)

    Full_Name = serializers.SerializerMethodField()

    def get_Full_Name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


    class Meta:
        model = Barber
        fields ='__all__'


class BarberStatsSerializer(serializers.Serializer):
    total_reviews = serializers.IntegerField()
    average_rating = serializers.FloatField()
    total_appointments = serializers.IntegerField()
    

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
    


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    profile_picture = serializers.ImageField(required=False)


    Full_Name = serializers.SerializerMethodField()

    def get_Full_Name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


    class Meta:
        model = Customer
        fields ='__all__'
class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

class SalonSerializer(serializers.ModelSerializer):
    barbers = serializers.PrimaryKeyRelatedField(queryset=Barber.objects.all(), many=True, required=False)
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = Salon
        fields = ['id', 'name', 'address', 'phone_number', 'profile_picture', 'barbers']


    def create(self, validated_data):
        barbers_data = validated_data.pop('barbers', [])  
        salon = Salon.objects.create(**validated_data)
        salon.barber.set(barbers_data)  
        return salon

    def update(self, instance, validated_data):
        barbers_data = validated_data.pop('barbers', [])  
        instance = super().update(instance, validated_data)
        instance.barber.set(barbers_data)  
        return instance
    
class LandingUPSerializer(serializers.ModelSerializer):
    class Meta:
        model =LandingUP
        fields = '__all__'
class LandingMidSerializer(serializers.ModelSerializer):
    class Meta:
        model =LandingMid
        fields = '__all__'

class LandingDownSerializer(serializers.ModelSerializer):
    class Meta:
        model =LandingDown
        fields = '__all__'

    
class LandingGifsSerializer(serializers.ModelSerializer):
    class Meta:
        model =LandingGifs
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'recipient_barber', 'rating', 'comment', 'created_at', 'images']
        read_only_fields = ['id', 'created_at','reviewer', 'recipient_barber']


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponseMessage
        fields = ['id', 'review', 'responder', 'reply', 'image', 'created_at', 'updated_at']
        read_only_fields = ('review', 'responder', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['responder'] = self.context['request'].user.barber
        return super().create(validated_data)
    

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'title', 'created_at']
        
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'text', 'reply', 'created_at']

        
class SendMessageSerializer(serializers.Serializer):
    text = serializers.CharField()

class BlockedTimesOfBarberSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedTimesOfBarber
        fields = ['start_time','end_time']

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'customer', 'services', 'barber', 'day','start_time', 'end_time', 'created_at']

class Appointment_Serializer(serializers.ModelSerializer):
     class Meta:
        model = Appointment
        fields = ['start_time', 'end_time']

class ServicesNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['name']
class AppointmentServicesNameSerializer(serializers.ModelSerializer):
    services = ServicesNameSerializer(many=True) 

    class Meta:
        model = Appointment
        fields = ['services','created_at']

