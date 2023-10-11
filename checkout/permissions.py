from rest_framework import permissions

from .models import PagarmeWebhook

class CreditOrderPermisions(permissions.BasePermission):
    def has_permission(self, request, view):
        return True
        
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if request.method in ['PUT','DELETE']:
            return False
        
        if request.method == 'PATCH':
            if obj.status != 1:
                return False

            forbidden_fields = ['user', 'credit_pack', 'payment_method']
            for forbidden_field in forbidden_fields:
                if forbidden_field in request.data:
                    return False
                

class PagarmeWebhookPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        try:
            return PagarmeWebhook.objects.get(pagarme_id=request.data['id'])
        except:
            return False
        
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        try:
            return PagarmeWebhook.objects.get(pagarme_id=request.data['id'])
        except:
            return False