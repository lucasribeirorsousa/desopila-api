from django.urls import path, include
from rest_framework import routers

from .views import (
    AddressViewSet,
    PlaceAdsViewSet,
    WeekDayViewSet,
    PlanViewSet,
)

router = routers.DefaultRouter()
router.register('address', AddressViewSet, basename='address')
router.register('days', WeekDayViewSet, basename='days')
router.register('places-ads', PlaceAdsViewSet, basename='places-ads')
router.register('plans', PlanViewSet, basename='plans')

urlpatterns = [
    path("",  include((router.urls, 'places'), namespace='places_urls')),
]
