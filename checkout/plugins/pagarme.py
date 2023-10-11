import os
from base64 import b64encode
from dotenv import load_dotenv

from checkout.plugins.base import GatewayBase
from checkout.models import Gateway, GatewayUser

from checkout.payment_settings import TOKEN_GATEWAY

load_dotenv()

GATEWAY = 'pagarme'
class Pagarme(GatewayBase):
    _token = TOKEN_GATEWAY
    _gateway, _ = Gateway.objects.get_or_create(name=GATEWAY)
    _base_url = 'https://api.pagar.me/core/v5'

    @property
    def headers(self):
        return {
            'Authorization': f"Basic {b64encode(bytes(f'{self._token}:', 'utf-8')).decode('utf-8')}",
            'Content-Type': 'application/json',
        }

    def create_customer(self, **kwargs):
        
        user = kwargs.get('user')
        address = kwargs.get('address')

        name = f"{user.first_name} {user.last_name}"
        
        if len(user.cpf_cnpj) > 11:
            document_type='CNPJ'
        else:
            document_type='CPF'
        
        customer_data = {
            'name': name,
            'email': user.email,
            'document': user.cpf_cnpj,
            'type': 'individual',
            'document_type': document_type,
            'address': {
                "line_1": address.map_string,
                "line_2": address.reference,  
                "zip_code": address.cep,
                "city": "N/A",
                "state": "N/A",
                "country": "BR"  
            },
            'phones': {
                'home_phone': {
                    'country_code': '55',
                    'area_code': user.phone[slice(0, 2)],
                    'number': user.phone[slice(2, 11)]
                },
            }
        }
        
        customer_request = self._request_api(method='POST', route='customers/', data=customer_data, headers=self.headers)
        customer_data = customer_request.json()

        if customer_request.status_code == 200:
            GatewayUser.objects.create(
                gateway=self._gateway,
                user=user,
                user_on_gateway_id=customer_data.get('id')
            )
            
            return customer_data

        return False


    def create_card(self, *args, **kwargs):
        gateway_user = kwargs.get('gateway_user')
        data = kwargs.get('data')
        address = kwargs.get('address')
        
        card_data = {
            "number": data['number'],
            "holder_name": data['holder_name'],
            "holder_document": data['holder_document'],
            "exp_month": data['exp_month'],
            "exp_year": data['exp_year'],
            "cvv": data['cvv'],
            "brand": data['brand'],
            "label": data['label'],
            "billing_address": {
                "line_1": address.map_string,
                "line_2": address.reference,  
                "zip_code": address.cep,
                "city": "N/A",
                "state": "N/A",
                "country": "BR"  
            },
            "options": {
                "verify_card": True
            }
        }

        response = self._request_api(
            method = 'POST',
            route = f'customers/{gateway_user.user_on_gateway_id}/cards',
            data = card_data,
            headers = self.headers
            )

        return response


    def delete_card(self, *args, **kwargs):
        gateway_user = kwargs.get('gateway_user')
        gateway_card = kwargs.get('gateway_card')
        
        response = self._request_api(
            method = 'DELETE',
            route = f'customers/{gateway_user.user_on_gateway_id}/cards/{gateway_card.card_on_gateway_id}',
            headers = self.headers
            )

        return response


    def create_order(self, *args, **kwargs):
        gateway_user = kwargs.get('gateway_user')
        payment_data = kwargs.get('payment_data')
        credit_order = kwargs.get('credit_order')

        order_data = {
            "items": [{
                "amount": int(credit_order.credit_pack.price * 100),
                "description": credit_order.credit_pack.name,
                "quantity": 1,
                "code": credit_order.credit_pack.id
            }],
            "customer_id": gateway_user.user_on_gateway_id,
            "payments": [payment_data],
            "closed": True,
            "antifraud_enabled": True,
        }
        
        response = self._request_api(
            method = 'POST',
            route = f'/orders',
            data = order_data,
            headers = self.headers
        )
        
        return response


    def credit_card_payment(self, *args, **kwargs):
        card = kwargs.get('card')
        gateway_user = kwargs.get('gateway_user')
        installments = kwargs.get('installments')
        credit_order=kwargs.get('credit_order')

        payment_data = {
            "payment_method": "credit_card",
            "credit_card": {
                "recurrence": False,
                "installments": installments,
                "statement_descriptor": "App Desopila",
                "operation_type": "auth_and_capture",
                "card_id": card.gateway_card_set.all()[0].card_on_gateway_id
            }
        }

        response = self.create_order(
            payment_data=payment_data,
            gateway_user=gateway_user,
            credit_order=credit_order
        )

        return response
