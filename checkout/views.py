import os
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import action

from places.models import Address
from .tasks import send_user_email
from .models import (
    Credit, 
    PagarmeWebhook,
    PaymentMethod, 
    CreditPack, 
    Card,
    Gateway,
    GatewayCard,
    GatewayUser,
    CreditOrder,
    GatewayCreditOrder,
)

from .serializers import (
    CreditSerializer,
    CreditPackSerializer,
    PaymentMethodSerializer,
    CardSerializer,
    CreditOrderSerializer,
    PagarmeWebhookSerializer,
)

from .permissions import CreditOrderPermisions, PagarmeWebhookPermission

from .plugins import gateway
GATEWAY = os.getenv('GATEWAY')

class CreditViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = CreditSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return Credit.objects.filter(user=self.request.user)


class PaymentMethodViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]


class CreditPackViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = CreditPack.objects.all()
    serializer_class = CreditPackSerializer
    permission_classes = [IsAuthenticated]


class CardViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = CardSerializer

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            gateway_user = GatewayUser.objects.get(user=request.user)
            address = Address.objects.get(id=data['billing_address'])
            
            gateway_card_request = gateway.create_card(gateway_user=gateway_user, data=data, address=address)
            gateway_card_data = gateway_card_request.json()
            
            if gateway_card_request.status_code != status.HTTP_200_OK:
                return Response(data={"gateway_error": gateway_card_data}, status=status.HTTP_400_BAD_REQUEST)
            
            card = Card.objects.create(
                user=request.user,
                brand=data['brand'],
                last_digits=data['number'][12:16],
                holder_name=data['holder_name'],
                billing_address=address
            )

            GatewayCard.objects.create(
                gateway=Gateway.objects.get(name=GATEWAY),
                card=card,
                card_on_gateway_id=gateway_card_data['id']
            )

            return Response(data=CardSerializer(instance=card).data, status=status.HTTP_201_CREATED)

        except Exception as error:
            transaction.set_rollback(True)
            raise ValidationError(error)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            gateway_user = GatewayUser.objects.get(user=request.user)
            card = self.get_object()
            gateway_card = GatewayCard.objects.get(card=card)

            gateway_card_delete_response = gateway.delete_card(gateway_user=gateway_user, gateway_card=gateway_card)
            gateway_card_delete_data = gateway_card_delete_response.json()

            if gateway_card_delete_response.status_code != status.HTTP_200_OK:
                return Response(data={"gateway_errors": gateway_card_delete_data['message']}, status=status.HTTP_400_BAD_REQUEST)

            gateway_card.delete()
            card.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as error:
            transaction.set_rollback(True)
            raise ValidationError(error)


class CreditOrderViewSet(viewsets.ModelViewSet):
    serializer_class = CreditOrderSerializer
    permission_classes = [IsAuthenticated, CreditOrderPermisions]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return CreditOrder.objects.all()
        return CreditOrder.objects.filter(user=self.request.user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            credit_pack = CreditPack.objects.get(id=request.data['credit_pack'])
            payment_method = PaymentMethod.objects.get(id=request.data['payment_method'])
            card = Card.objects.get(id=request.data['card'])

            credit_order = CreditOrder.objects.create(
                user = request.user,
                credit_pack = credit_pack ,
                payment_method = payment_method,
                card = card,
            )

            payment_response = gateway.credit_card_payment(
                credit_order=credit_order,
                card=card,
                gateway_user=GatewayUser.objects.get(user=request.user),
                installments=request.data.get('installments', 1),
            )

            if payment_response.status_code != status.HTTP_200_OK:
                transaction.set_rollback(True)
                raise ValidationError({"erro": "Erro na gateway de pagamento"})
            
            if payment_response.json()['charges'][0]['last_transaction']['gateway_response']['code'] != '200':
                transaction.set_rollback(True)
                raise ValidationError({
                    "message": "Order created, but with status failed", 
                    "errors": payment_response.json()['charges'][0]['last_transaction']['gateway_response']['errors'],
                })

            GatewayCreditOrder.objects.create(
                gateway=Gateway.objects.get(name=GATEWAY),
                credit_order=credit_order,
                credit_order_on_gateway_id=payment_response.json()['id']
            )

            send_user_email(
                email=request.user.email,
                title="Compra de creditos aguardando pagamento",
                message="Estamos aguardando o pagamento para adicionar seus créditos. Caso o pagamento não seja realizado sua compra será cancelada."
            )

            return Response(data=CreditOrderSerializer(instance=credit_order).data, status=status.HTTP_201_CREATED)

        except Exception as error:
            transaction.set_rollback(True)
            raise ValidationError(error)


class PagarmeWebhookViewSet(viewsets.ModelViewSet):
    queryset = PagarmeWebhook.objects.all()
    serializer_class = PagarmeWebhookSerializer
    permission_classes = [PagarmeWebhookPermission]

    @transaction.atomic
    @action(methods=['POST'], detail=False, url_path='order-paid')
    def order_paid_webhook(self, request, *args, **kwargs):
        try:
            credit_order = GatewayCreditOrder.objects.get(credit_order_on_gateway_id=request.data['data']['id']).credit_order

            if credit_order.status != 1:
                raise ValidationError({ "message": "Order already completed"})

            credit_order.status = 2
            credit_order.save()

            credit = Credit.objects.get(user=credit_order.user)
            credit.amount += credit_order.credit_pack.price
            credit.save()
            
            send_user_email(
                "Compra de créditos concluída",
                "Seu pagamento foi realizado e seus créditos já foram adicionados à sua conta!!!\n Obrigado por usar nosso aplicativo.",
                credit_order.user.email,
            )

            return Response(status=status.HTTP_200_OK)
        except Exception as error:
            transaction.set_rollback(True)
            raise ValidationError(error)

    @transaction.atomic
    @action(methods=['POST'], detail=False, url_path='order-canceled')
    def order_canceled_webhook(self, request, *args, **kwargs):
        try:
            credit_order = GatewayCreditOrder.objects.get(credit_order_on_gateway_id=request.data['data']['id']).credit_order
            credit_order.status = 3
            credit_order.save()

            send_user_email(
                email=request.user.email,
                title="Compra de créditos cancelada",
                message="Infelizmente sua compra foi cancelada."
            )

            return Response(status=status.HTTP_200_OK)
        except Exception as error:
            transaction.set_rollback(True)
            raise ValidationError(error)