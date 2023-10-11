from rest_framework import serializers
from django.forms.models import model_to_dict

from asset.serializers import AssetSerializer
from .models import (
    Address,
    WeekDay,
    PlaceAds,
    Plan,
)



class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class WeekDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = WeekDay
        fields = '__all__'


class PlaceAdsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PlaceAds
        fields = '__all__'

    def to_representation(self, instance):
        plan_data = []
        plans = Plan.objects.filter(place_ads=instance)
        
        for i, plan in enumerate(plans):
            plan_data.append(model_to_dict(plan))
            plan_data[i] = PlanSerializer(instance=plan).data

        images_data = []
        images = instance.images.all()

        for i, image in enumerate(images):
            images_data.append(model_to_dict(image))
            images_data[i] = AssetSerializer(instance=image).data


        return{
            "id": instance.id,
            "user": instance.user.id,
            "place_title": instance.place_title,
            "place_description": instance.place_description,
            "local_type": instance.local_type,
            "capacity": instance.capacity,
            "status": instance.status,
            "created_at": instance.created_at,
            "address": AddressSerializer(instance=instance.address).data,
            "plans": plan_data,
            "images": images_data
        }


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'