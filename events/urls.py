from django.urls import path, include
from rest_framework import routers

from .views import (
    EventOrderViewSet, 
    CancellationViewSet, 
    HistoryViewSet, 
    RefuseOrderViewSet,
    AcceptOrderViewSet,
    UpdateDatesSelectedViewSet
)

router = routers.DefaultRouter()
router.register('event-orders', EventOrderViewSet, basename='event-orders')
router.register('event-histories', HistoryViewSet, basename='event-histories')
router.register('cancellations', CancellationViewSet, basename='cancellations')

urlpatterns = [
    path("",  include((router.urls, 'events'), namespace='events_urls')),
    path("accept-order/", AcceptOrderViewSet.as_view(), name='accept-order'),
    path("refuse-order/", RefuseOrderViewSet.as_view(), name='refuse-order'),
    path("dates-selected-update/", UpdateDatesSelectedViewSet.as_view(), name='dates-selected-update'),
]
