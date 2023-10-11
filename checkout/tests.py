import os, tempfile
from PIL import Image
from rest_framework.test import APITestCase
from model_bakery import baker
from django.urls import reverse
from rest_framework import status

from checkout.models import Card, Credit, CreditOrder, Gateway, GatewayCard, Gateway, GatewayUser
from authentication.models import User

GATEWAY = 'pagarme'

class GatewayTests(APITestCase):
    def test_create_gateway(self):
        gateway = baker.make('checkout.Gateway', name=os.getenv('GATEWAY'))
        self.assertEquals(Gateway.objects.get().name, gateway.name)


class CardTests(APITestCase):
    
    def setUp(self) -> None:
        if not Gateway.objects.filter(name=GATEWAY).exists():
            self.gateway = baker.make('checkout.Gateway', name=GATEWAY, id=2)
        else:
            self.gateway = Gateway.objects.get(name=GATEWAY)

        body = {
            "address": {
                "map_string": "Rua das Carlotas, 123",
                "reference": "Em frente ao atacado varejo",
                "cep": "84268660",
                "latitude": -5.820903,
                "longitude": -35.188911
            },
            "cpf_cnpj": "96958343026",
            "email": "user@hotmail.com",
            "username": "user",
            "phone": "84988887578",
            "whatsapp": "84988887578",
            "first_name": "user",
            "last_name": "user",
            "password": "user"
        }
        
        url = f"{reverse('authentication_urls:users-list')}"
        self.client.post(url, body, format='json')

        self.user = User.objects.get(email=body['email'])
        self.gateway_user = GatewayUser.objects.get(user=self.user)
        self.address = baker.make(
            'places.Address',
            map_string="Map Street String",
            reference="reference",
            cep="84268660",
            latitude="4532534254",
            longitude="5432543"
        )

    def test_create_card(self):
        body = {
            "number": "4000000000000010",
            "holder_name": "Tony Stark",
            "holder_document": "96958343026",
            "exp_month": 1,
            "exp_year": 30,
            "cvv": "351",
            "brand": "Mastercard",
            "label": "renner",
            "billing_address": self.address.id
        }

        self.client.force_authenticate(self.user)
        url = f"{reverse('checkout_urls:card-list')}"
        response = self.client.post(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Card
        card = Card.objects.get()
        self.assertEqual(card.user, self.user)
        self.assertEqual(card.brand, body['brand'])
        self.assertEqual(card.last_digits, body['number'][12:16])
        self.assertEqual(card.holder_name, body['holder_name'])

        # Address
        self.assertEqual(card.billing_address.id, self.address.id)

        # GatewayCard        
        gateway_card = GatewayCard.objects.get()
        self.assertEqual(gateway_card.gateway, self.gateway)
        self.assertEqual(gateway_card.card, card)
        self.assertNotEqual(gateway_card.card_on_gateway_id, None)

    def test_present_errors_if_card_creation_fails(self):
        body = {
            "number": "4000000000000010",
            "holder_name": "Tony 2",
            "holder_document": "12345678910",
            "exp_month": 1,
            "exp_year": 30,
            "cvv": "351",
            "brand": "Mastercard",
            "label": "renner",
            "billing_address": self.address.id
        }

        self.client.force_authenticate(self.user)
        url = f"{reverse('checkout_urls:card-list')}"
        response = self.client.post(url, body, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(len(response.data['gateway_error']), 0)

    def test_list_just_the_user_cards(self):
        card = baker.make('checkout.Card', user=self.user)
        baker.make('checkout.Card')
        baker.make('checkout.Card')

        self.client.force_authenticate(self.user)
        url = f"{reverse('checkout_urls:card-list')}"
        response = self.client.get(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], card.id)

    def test_dont_list_a_specific_card_from_another_user(self):
        card1 = baker.make('checkout.Card', user=self.user)
        card2 = baker.make('checkout.Card')

        self.client.force_authenticate(self.user)
        url = f"{reverse('checkout_urls:card-list')}{card2.id}/"
        response = self.client.get(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_card(self):
        body = {
            "number": "4000000000000010",
            "holder_name": "Tony Stark",
            "holder_document": "96958343026",
            "exp_month": 1,
            "exp_year": 30,
            "cvv": "351",
            "brand": "Mastercard",
            "label": "renner",
            "billing_address": self.address.id
        }

        self.client.force_authenticate(self.user)
        url = f"{reverse('checkout_urls:card-list')}"
        response = self.client.post(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GatewayCard.objects.filter(card__id=response.data['id']).exists(), True)
        self.assertEqual(Card.objects.filter(id=response.data['id']).exists(), True)

        url = f"{reverse('checkout_urls:card-list')}{response.data['id']}/"
        response2 = self.client.delete(url, {}, format='json')

        self.assertEqual(response2.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(GatewayCard.objects.filter(card__id=response.data['id']).exists(), False)
        self.assertEqual(Card.objects.filter(id=response.data['id']).exists(), False)


class CreditTests(APITestCase):
    def setUp(self) -> None:
        self.user = baker.make('authentication.User')
        self.credits = baker.make('checkout.Credit', user=self.user)
        return super().setUp()

    def test_list_just_the_user_credits(self):
        self.client.force_authenticate(self.user)
        url = f"{reverse('checkout_urls:credit-list')}"
        response = self.client.get(url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.credits.id)
        self.assertEqual(len(response.data['results']), 1)

    def test_dont_create_credits(self):
        self.client.force_authenticate(self.user)
        url = f"{reverse('checkout_urls:credit-list')}"
        response = self.client.post(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_dont_delete_credits(self):
        self.client.force_authenticate(self.user)
        url = f"{reverse('checkout_urls:credit-list')}"
        response = self.client.delete(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_dont_update_credits(self):
        self.client.force_authenticate(self.user)
        url = f"{reverse('checkout_urls:credit-list')}"
        response = self.client.patch(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class CreditOrderTests(APITestCase):   
    def setUp(self) -> None:
        if not Gateway.objects.filter(name=GATEWAY).exists():
            self.gateway = baker.make('checkout.Gateway', name=GATEWAY, id=2)
        else:
            self.gateway = Gateway.objects.get(name=GATEWAY)

        image = Image.new(mode='RGB', size=(200, 20), color='blue')
        tmp_file = tempfile.NamedTemporaryFile(suffix='.png')
        image.save(tmp_file)
        tmp_file.seek(0)

        asset = baker.make('asset.Asset', file_high=tmp_file)
        body = {
            "asset": asset.id,
            "address": {
                "map_string": "Rua das Carlotas, 123",
                "reference": "Em frente ao atacado varejo",
                "cep": "65056229",
                "latitude": -5.820903,
                "longitude": -35.188911
            },
            "cpf_cnpj": "44581208084",
            "email": "user@hotmail.com",
            "username": "user",
            "phone": "84988887777",
            "whatsapp": "84988887777",
            "first_name": "New",
            "last_name": "User",
            "password": "user",
        }

        url = reverse('authentication_urls:users-list')
        self.client.post(url, body, format='json') # Creating user, credit, gateway_user


        self.user = User.objects.get()
        self.credit_pack = baker.make('checkout.CreditPack', price=20, credit_amount=100)
        self.payment_method = baker.make('checkout.PaymentMethod', method=1)
        self.address = baker.make(
            'places.Address',
            map_string="Map Street String",
            reference="reference",
            cep="65056229",
            latitude="4532534254",
            longitude="5432543"
        )

        body = {
            "number": "4000000000000010",
            "holder_name": "Tony Stark",
            "holder_document": "96958343026",
            "exp_month": 1,
            "exp_year": 30,
            "cvv": "351",
            "brand": "Mastercard",
            "label": "renner",
            "billing_address": self.address.id
        }

        self.client.force_authenticate(self.user)
        url = f"{reverse('checkout_urls:card-list')}"
        self.client.post(url, body, format='json') # Creating card and gateway_card
        
        self.card = Card.objects.get()
        self.credits = Credit.objects.get(user=self.user, amount=0)

        return super().setUp()

    def create_credit_order(self):
        body = {
            "credit_pack": self.credit_pack.id,
            "card": self.card.id,
            "payment_method": self.payment_method.id,
            "installments":1
        }

        self.client.force_authenticate(self.user)
        url = f"{reverse('checkout_urls:credit-order-list')}"
        response = self.client.post(url, body, format='json')
        
        # Credit_Order
        self.credit_order = CreditOrder.objects.get()

        return response

    def test_create_credit_order(self):
        response = self.create_credit_order()
        
        credit_order = CreditOrder.objects.get()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(credit_order.status, 1)
        self.assertEqual(credit_order.user, self.user)
        self.assertEqual(credit_order.credit_pack, self.credit_pack)
        self.assertEqual(credit_order.payment_method, self.payment_method)
        self.assertEqual(credit_order.card, self.card)
        
    def test_order_paid_webhook(self):
        self.create_credit_order()

        body = {
            "data":{
                "code": self.credit_order.id
            }
        }

        self.client.force_authenticate(self.user)
        url = f"{reverse('checkout_urls:credit-order-order-paid-webhook')}"
        response = self.client.patch(url, body, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_canceled_webhook(self):
        self.create_credit_order()

        body = {
            "data":{
                "code": self.credit_order.id
            }
        }

        self.client.force_authenticate(self.user)
        url = f"{reverse('checkout_urls:credit-order-order-canceled-webhook')}"
        response = self.client.patch(url, body, format='json')
        