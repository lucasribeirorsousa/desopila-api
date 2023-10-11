# import os
from checkout.models import Gateway
from dotenv import load_dotenv

from checkout.plugins.base import GatewayBase

load_dotenv()

GATEWAY = 'mercado_pago'

class MercadoPago(GatewayBase):
    _base_url = f'https://mercado-pago/api'
    _gateway, _ = Gateway.objects.get_or_create(name=GATEWAY)
    # _token = os.getenv('TOKEN_MERCADO_PAGO_TEST')

    def create_customer(self, *args, **kwargs):
        pass

    def create_receiver(self, *args, **kwargs):
        pass

    def create_card(self, *args, **kwargs):
        pass