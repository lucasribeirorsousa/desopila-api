from rest_framework import serializers

from .models import Credit, CreditPack, PaymentMethod, Card, CreditOrder, PagarmeWebhook
from places.serializers import AddressSerializer

class CreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credit
        fields = '__all__'


class CreditPackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditPack
        fields = '__all__'


class PagarmeWebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagarmeWebhook
        fields = '__all__'


class CreditOrderSerializer(serializers.ModelSerializer):
    installments = serializers.IntegerField(read_only=True, label="Parcelas")

    class Meta:
        model = CreditOrder
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['credit_pack'] = CreditPackSerializer()
        self.fields['payment_method'] = PaymentMethodSerializer()
        return super().to_representation(instance)


class PaymentMethodSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentMethod
        fields = '__all__'


class CardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Card
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['billing_address'] = AddressSerializer()
        return super(CardSerializer, self).to_representation(instance)

