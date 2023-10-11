from rest_framework import permissions
from rest_framework.exceptions import ValidationError

from events.models import EventOrder
from places.models import PlaceAds


class EventOrderPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if request.method == 'POST': 
            place_ads = PlaceAds.objects.get(id=request.data['place_ads'])
            if request.user == place_ads.user:
                return False

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        elif request.method in permissions.SAFE_METHODS:
            return obj.user == request.user or obj.place_ads.user == request.user
        
        else:
            return False


class CancellationPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            if request.method in permissions.SAFE_METHODS:
                return request.user.is_authenticated 

            if request.method in ['POST']:
                event_order = EventOrder.objects.get(id=request.data['event_order'])
                user_orderer = event_order.user
                user_owner = event_order.place_ads.user
                return request.user.is_authenticated and (user_orderer == request.user or user_owner == request.user)

        except Exception as error:
            raise ValidationError(error)


class UpdateStatusPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            if request.method in ['PATCH']:
                event_order = EventOrder.objects.get(id=request.data['event_order'])
                user_owner = event_order.place_ads.user
                return request.user.is_authenticated and user_owner==request.user
        
        except Exception as error:
            raise ValidationError(error)


class UpdateDatesSelectedPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            if request.method in ['PATCH']:
                event_order = EventOrder.objects.get(id=request.data['event_order'])
                user_orderer = event_order.user
                return request.user.is_authenticated and user_orderer == request.user 
        
        except Exception as error:
            raise ValidationError(error)