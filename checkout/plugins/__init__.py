from aluguel_api.settings import GATEWAY

from .mercado_pago import MercadoPago
from .pagarme import Pagarme

gateways = {
    'mercado_pago': MercadoPago(),
    'pagarme': Pagarme(),
}

gateway = gateways[GATEWAY]
