from django.urls import path, include
from rest_framework import routers

from .views import (
    CreditPackViewSet, 
    CreditViewSet, 
    PaymentMethodViewSet, 
    CreditOrderViewSet,
    CardViewSet,
    PagarmeWebhookViewSet
)

router = routers.DefaultRouter()
router.register('credit', CreditViewSet, basename='credit')
router.register('credit-pack', CreditPackViewSet, basename='credit-pack')
router.register('payment-method', PaymentMethodViewSet, basename='payment-method')
router.register('credit-order', CreditOrderViewSet, basename='credit-order')
router.register('card', CardViewSet, basename='card')
router.register('pagarme-webhook', PagarmeWebhookViewSet, basename='pagarme-webhook')


urlpatterns = [
    path("", include((router.urls, 'checkout'), namespace='checkout_urls')),
]