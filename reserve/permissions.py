from rest_framework import permissions
from .models import *

class IsBarberAdminSalonWithJWT(permissions.BasePermission):
    """
    Allows access only to barber users with a valid JWT and is_admin=True.
    """


    def has_permission(self, request, view):
        if request.user.is_authenticated and hasattr(request.user, 'barber') and request.user.barber.is_admin:
            if view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
                return True
        return False
    

class CanRespondToReview(permissions.BasePermission):
    """
    Allows access only to salon owners with a valid JWT and are the owner of the salon associated with the review.
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated and hasattr(request.user, 'barber') and request.user.barber.is_admin:
            print(request.data)
            review_id = view.kwargs.get('review_id')  # Assuming the review ID is passed in the request data
            if review_id:
                try:
                    review = Review.objects.get(pk=review_id)
                    return True
                except Review.DoesNotExist:
                    return False  # Review does not exist, permission denied
        return False


class IsBarberAdminSalonWithJWTForUpdate(permissions.BasePermission):
    """
    Allows access only to barber users with a valid JWT and is_admin=True.
    """

    def has_permission(self, request, view):
        print("Checking permissions...")
        if request.user.is_authenticated and hasattr(request.user, 'barber') and request.user.barber:
            print("User is authenticated and has a Barber instance.")
            if request.user.barber.is_admin:
                print("User is an admin.")
                salon_id = view.kwargs.get('pk')
                if salon_id:
                    print("Salon ID:", salon_id)
                    try:
                        salon = Salon.objects.get(pk=salon_id)
                    except Salon.DoesNotExist:
                        print("Salon does not exist.")
                        return False
                    print("Salon exists.")
                    if request.user.barber.salons is not None:
                        print(request.user.barber.salons)
                    else:
                        print("Barber has no salons.")
                    print(salon_id)
                    return True
        print("Permissions denied.")
        return False
    
class IsUserOwnerWithJWT(permissions.BasePermission):
    """
    Allows access only to the user who owns the profile with a valid JWT.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the request is authenticated with a valid JWT and the user is the owner of the profile
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user == obj.user)
        )
    
class IsBarberOwnerWithJWT(permissions.BasePermission):
    """
    Allows access only to barber users with a valid JWT and ownership of the profile.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the user is a barber and has a valid JWT
        is_barber = hasattr(request.user, 'barber')
        has_valid_jwt = request.user.is_authenticated

        is_owner = obj.user == request.user
        # Print debug information
        print(f"User: {request.user}")
        print(f"Is authenticated: {request.user.is_authenticated}")
        print(f"Is barber: {is_barber}")
        print(f"Barber profile: {request.user.barber if is_barber else None}")
        print(f"Object: {obj}")
        print(f"Is owner: {is_owner}")
        return is_barber and has_valid_jwt and is_owner


class IsCustomerOwnerWithJWT(permissions.BasePermission):
    """
    Allows access only to customer users with a valid JWT and ownership of the profile.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the user is a customer and has a valid JWT
        is_customer = hasattr(request.user, 'customer')
        has_valid_jwt = request.user.is_authenticated

        # Check if the user is the owner of the profile
        return is_customer and has_valid_jwt and obj == request.user.customer