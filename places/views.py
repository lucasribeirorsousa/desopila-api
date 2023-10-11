from rest_framework import filters, viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import (
    Address,
    WeekDay,
    PlaceAds,
    Plan,
)
from .serializers import (
    AddressSerializer,
    PlaceAdsSerializer,
    PlanSerializer,
    WeekDaySerializer,
)
from .permissions import (
    PlaceAdsPermissions,
)
from .filters import(
    LocalTypeFilter,
    UserFilter,
    StatusFilter,
)


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

class WeekDayViewSet(viewsets.ModelViewSet):
    queryset = WeekDay.objects.all()
    serializer_class = WeekDaySerializer


class PlaceAdsViewSet(viewsets.ModelViewSet):
    queryset = PlaceAds.objects.all()
    serializer_class = PlaceAdsSerializer
    permission_classes = [PlaceAdsPermissions]
    search_fields = ['place_title', 'place_description']
    filter_backends = [
        LocalTypeFilter,
        UserFilter,
        StatusFilter,
        filters.SearchFilter,
    ]

    def create(self, request, *args, **kwargs):
        try:
            request_address = request.data['address']
            address = Address.objects.create(**request_address)
            
            try:
                request_status = request.data['status']
            except:
                request_status = 1
            
            place_ads = PlaceAds.objects.create(
                user=request.user,
                address=address,
                place_title=request.data['place_title'],
                place_description=request.data['place_description'],
                local_type=request.data['local_type'],
                capacity=request.data['capacity'],
                status=request_status
                )
            
            through_objs = []
            for image_id in request.data['images']:
                throug = PlaceAds.images.through(asset_id=image_id, placeads_id=place_ads.id)
                through_objs.append(throug)

            PlaceAds.images.through.objects.bulk_create(through_objs)

            request_plans = request.data['plans']
            
            all_week_days_obj = WeekDay.objects.all()
            for request_plan in request_plans:
                week_days_id_list = [
                    all_week_days_obj.get(day=week_day).id
                    for week_day in request_plan['week_days']
                ]

                plan = Plan.objects.create(
                    place_ads=place_ads,
                    plan_type=request_plan['plan_type'],
                    name=request_plan['name'],
                    price=request_plan['price'],
                )
                
                through_objs = []
                for day_id in week_days_id_list:
                    throug = Plan.week_days.through(
                        weekday_id=day_id,
                        plan_id=plan.id,
                    )
                    through_objs.append(throug)
            
                Plan.week_days.through.objects.bulk_create(through_objs)

            return Response(data=self.serializer_class(instance=place_ads).data, status=status.HTTP_201_CREATED)

        except Exception as error:
            raise ValidationError(error)

    def update(self, request, *args, **kwargs):
        try:
            request_address = request.data['address']
            address = Address.objects.get(id=request_address['id'])

            #update address
            address.map_string = request_address['map_string']
            address.reference = request_address['reference']
            address.cep = request_address['cep']
            address.latitude = request_address['latitude']
            address.longitude = request_address['longitude']
            address.save()
            
            #update place_ads
            place_ads = self.get_object()
            place_ads.place_title = request.data['place_title']
            place_ads.place_description = request.data['place_description']
            place_ads.local_type = request.data['local_type']
            place_ads.capacity = request.data['capacity']
            place_ads.place_title = request.data['place_title']
            place_ads.images.set(request.data['images'])
            place_ads.save()
            
            #update plan
            plans = Plan.objects.filter(place_ads=place_ads)
            request_plans = request.data['plans']
            
            new_plans_id = []
            all_week_days_obj = WeekDay.objects.all()
            for request_plan in request_plans:
                try:
                    week_days_list = []
                    
                    for day in request_plan['week_days']:
                        day_id = all_week_days_obj.get(day=day).id
                        week_days_list.append(day_id)
                    
                    plan = plans.get(id=request_plan['id'])
                    plan.plan_type = request_plan['plan_type']
                    plan.name = request_plan['name']
                    plan.price = request_plan['price']
                    plan.week_days.set(week_days_list)
                    plan.save()

                except:
                    week_days_id_list = [
                        all_week_days_obj.get(day=week_day).id
                        for week_day in request_plan['week_days']
                    ]

                    plan = Plan.objects.create(
                        place_ads=place_ads,
                        plan_type=request_plan['plan_type'],
                        name=request_plan['name'],
                        price=request_plan['price'],
                    )
                    
                    through_objs = []
                    for day_id in week_days_id_list:
                        throug = Plan.week_days.through(
                            weekday_id=day_id,
                            plan_id=plan.id,
                        )
                        through_objs.append(throug)
                
                    Plan.week_days.through.objects.bulk_create(through_objs)

                
                new_plans_id.append(plan.id)

            
            for plan in plans:
                
                if not plan.id in new_plans_id:
                    plan.delete()

            return Response(data=self.serializer_class(instance=place_ads).data, status=status.HTTP_200_OK)
        except Exception as error:
            raise ValidationError(error)


class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer