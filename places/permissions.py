from rest_framework import permissions


class PlaceAdsPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method in ['POST', 'PUT', 'DELETE']:
            if request.method in ['POST', 'PUT']:
                request.data['user']=request.user.id
            return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        
        if request.user.is_superuser:
            return True
        
        elif request.method in permissions.SAFE_METHODS:
            return True
        
        
        elif request.method in ['PUT', 'DELETE']:
            return obj.user == request.user
        
        else:
            return False
