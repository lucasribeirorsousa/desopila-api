from rest_framework import viewsets, status
from rest_framework import mixins
from django.db.models import Q
from datetime import datetime
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from checkout.models import Credit

from places.models import Plan, PlaceAds

from .models import EventOrder, Cancellation, History
from .serializers import (
    EventOrderSerializer,
    CancellationSerializer,
    HistorySerializer,
    AcceptOrderSerializer,
    RefuseOrderSerializer,
    UpdateDatesSelectedSerializer,
    EventOrderListSerializer,
)
from .permissions import (
    CancellationPermissions,
    EventOrderPermissions,
    UpdateStatusPermissions,
    UpdateDatesSelectedPermissions,
)
from checkout.constants import UNLOCK_PRICE
class EventOrderViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet):

    queryset = EventOrder.objects.all()
    serializer_class = EventOrderSerializer
    permission_classes = [EventOrderPermissions]
    filterset_fields = ['place_ads']

    def create(self, request, *args, **kwargs):
        try:            
            serializer = self.serializer_class(data=request.data)            
            serializer.is_valid(raise_exception=True)
            
            data = request.data
            plan = Plan.objects.get(id=data['plan'])
            plan_type = plan.plan_type
            
            plan_week_days_number_list = []
            for week_day_obj in plan.week_days.all():
                plan_week_days_number_list.append(week_day_obj.day)

            dates_selected = []
            event_week_days_number = []
            for timestamp in data['dates_selected']:
                date = datetime.fromtimestamp(timestamp)
                dates_selected.append(date)
                event_week_days_number.append(date.weekday())

            if plan_type == 1  and set(event_week_days_number) <= set(plan_week_days_number_list):   #daily
                price = plan.price * len(data['dates_selected'])
            
            if plan_type == 2  and set(event_week_days_number) == set(plan_week_days_number_list):   #package
                price = plan.price

            event_order = EventOrder.objects.create(
                user=request.user,
                place_ads=PlaceAds.objects.get(id=data['place_ads']),
                dates_selected=dates_selected,
                title=data['title'],
                description=data['description'],
                price=price,
                plan_type=plan_type,
            )
            
            return Response(data=self.serializer_class(instance=event_order).data, status=status.HTTP_201_CREATED)
        
        except Exception as error:
            raise ValidationError(error)

    def list(self, request, *args, **kwargs):
        self.serializer_class = EventOrderListSerializer
        self.queryset = EventOrder.objects.filter(Q(user=request.user) | Q(place_ads__user=request.user))
        return super().list(request, *args, **kwargs)


class CancellationViewSet(viewsets.ModelViewSet):
    queryset = Cancellation.objects.all()
    serializer_class = CancellationSerializer
    permission_classes = [CancellationPermissions]

    def create(self, request, *args, **kwargs):
        try:            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            event_order = EventOrder.objects.get(id=request.data['event_order'])
            event_order.status = 4
            event_order.save()
            
            cancellation = Cancellation.objects.create(
                event_order=event_order,
                justification=request.data['justification']
            )
            return Response(data=self.serializer_class(instance=cancellation).data, status=status.HTTP_201_CREATED)

        except Exception as error:
            raise ValidationError(error)

    def list(self, request, *args, **kwargs):
        self.queryset = Cancellation.objects.filter(Q(event_order__user=request.user) | Q(event_order__place_ads__user=request.user))
        return super().list(request, *args, **kwargs)


class HistoryViewSet(viewsets.ModelViewSet):
    queryset = History.objects.all()
    serializer_class = HistorySerializer


class AcceptOrderViewSet(APIView):
    serializer_class = AcceptOrderSerializer
    permission_classes = [UpdateStatusPermissions]

    def patch(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            event_order = EventOrder.objects.get(id=request.data['event_order'])
            credit = Credit.objects.get(user=request.user)

            if credit.amount - UNLOCK_PRICE >= 0:
                credit.amount -= UNLOCK_PRICE
                credit.save()
                
                event_order.status = 2
                event_order.save()
            
                data = {"message": "Evento aceito"}
                return Response(data=data, status=status.HTTP_200_OK)
            
            else: 
                raise ValidationError(f"Créditos insuficientes.")
        except Exception as error:
            raise ValidationError(error)


class RefuseOrderViewSet(APIView):
    serializer_class = RefuseOrderSerializer
    permission_classes = [UpdateStatusPermissions]

    def patch(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            event_order = EventOrder.objects.get(id=request.data['event_order'])
            event_order.status = 3
            event_order.save()
            
            data = {"message": "Evento recusado."}
            return Response(data=data, status=status.HTTP_200_OK)
        except Exception as error:
            raise ValidationError(error)


class UpdateDatesSelectedViewSet(APIView):
    serializer_class = UpdateDatesSelectedSerializer
    permission_classes = [UpdateDatesSelectedPermissions]

    def patch(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            event_order = EventOrder.objects.get(id=request.data['event_order'])
            plan = Plan.objects.get(id=request.data['plan'])

            dates_selected = []
            for timestamp in request.data['dates_selected']:
                date = datetime.fromtimestamp(timestamp)
                dates_selected.append(date)

            if event_order.plan_type == 1:     #daily
                price = plan.price * len(request.data['dates_selected'])
            
            if event_order.plan_type == 2:     #package
                price = plan.price

            event_order.dates_selected = dates_selected
            event_order.price = price
            event_order.save()

            data = {"message": "Datas alteradas."}
            return Response(data=data, status=status.HTTP_200_OK)

        except Exception as error:
            raise ValidationError(error)