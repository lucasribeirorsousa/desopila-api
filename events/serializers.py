from datetime import datetime
from rest_framework import serializers
from places.models import Plan

from places.serializers import PlaceAdsSerializer

from .models import EventOrder, Cancellation, History


class EventOrderSerializer(serializers.ModelSerializer):
    plan = serializers.IntegerField(write_only=True, label="Plano")
    dates_selected = serializers.ListField(child=serializers.FloatField(), write_only=True)
    price = serializers.FloatField(read_only=True, label="Preço")
    plan_type = serializers.IntegerField(read_only=True, label="Tipo de plano")
    user = serializers.PrimaryKeyRelatedField(read_only=True, label="Usuário")

    class Meta:
        model = EventOrder
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['place_ads'] = PlaceAdsSerializer(many=False, read_only=True)
        return super().to_representation(instance)

    def validate(self, data):
        plan = Plan.objects.get(id=data['plan'])
        place_ads = data['place_ads']

        plan_week_days_number_list = []
        for week_day_obj in plan.week_days.all():
            plan_week_days_number_list.append(week_day_obj.day)

        event_week_days_number = []
        for timestamp in data['dates_selected']:
            date = datetime.fromtimestamp(timestamp)
            event_week_days_number.append(date.weekday())

        if not plan.place_ads == place_ads:
            raise serializers.ValidationError("O plano selecionado não pertencem ao evento.")

        if plan.plan_type == 1  and not(set(event_week_days_number) <= set(plan_week_days_number_list)):     #daily
            raise serializers.ValidationError("Os dias selecionados devem estar dentro dos dias da semana que funcionam como diárias.")

        if plan.plan_type == 2  and not(set(event_week_days_number) == set(plan_week_days_number_list)):     #package
            raise serializers.ValidationError("Os dias selecionados devem ser do mesmo dia da semana do plano desejado.")
        
        return data

class EventOrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventOrder
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['place_ads'] = PlaceAdsSerializer(many=False, read_only=True)
        return super().to_representation(instance)

class CancellationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cancellation
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['event_order'] = EventOrderSerializer(many=False, read_only=True)
        return super().to_representation(instance)

    def validate(self, data):        
        event_order = data['event_order']
        if not event_order.status in [1,2]: 
            raise serializers.ValidationError("A ordem de evento não pode mais ser cancelada.")
        return data


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = '__all__'

class AcceptOrderSerializer(serializers.Serializer):
    event_order = serializers.IntegerField(write_only=True, )
    
    def validate(self, data):
        event_order = EventOrder.objects.get(id=data['event_order'])

        if not event_order.status == 1: 
            raise serializers.ValidationError(f"A ordem de evento não pode mais ser aceita.")

        return data

class RefuseOrderSerializer(serializers.Serializer):
    event_order = serializers.IntegerField(write_only=True, )
    
    def validate(self, data):
        event_order = EventOrder.objects.get(id=data['event_order'])
        
        if not event_order.status == 1: 
            raise serializers.ValidationError(f"A ordem de evento não pode mais ser recusada.")

        return data


class UpdateDatesSelectedSerializer(serializers.Serializer):
    dates_selected = serializers.ListField(child=serializers.FloatField())
    event_order = serializers.IntegerField(write_only=True)
    plan = serializers.IntegerField(write_only=True)

    def validate(self, data):
        event_order = EventOrder.objects.get(id=data['event_order'])
        plan = Plan.objects.get(id=data['plan'])

        plan_week_days_number_list = []
        for week_day_obj in plan.week_days.all():
            plan_week_days_number_list.append(week_day_obj.day)

        event_week_days_number = []
        for timestamp in data['dates_selected']:
            date = datetime.fromtimestamp(timestamp)
            event_week_days_number.append(date.weekday())
        
        if not event_order.status == 1: 
            raise serializers.ValidationError(f"Os dias selecionados não podem mais ser mudados pois o status atual é {event_order.status}")
        
        if not plan.place_ads == event_order.place_ads:
            raise serializers.ValidationError("O plano selecionado não pertencem ao evento.")

        if not plan.plan_type == event_order.plan_type:
            raise serializers.ValidationError("Tipo de plano divergente do plano cadastrado.")

        if event_order.plan_type == 1  and not(set(event_week_days_number) <= set(plan_week_days_number_list)):     #daily
            raise serializers.ValidationError("Os dias selecionados devem estar dentro dos dias da semana que funcionam como diárias.")

        if event_order.plan_type == 2  and not(set(event_week_days_number) == set(plan_week_days_number_list)):     #package
            raise serializers.ValidationError("Os dias selecionados devem ser do mesmo dia da semana do plano desejado.")
        
        return data
