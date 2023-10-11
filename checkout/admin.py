from django.contrib import admin
from .models import Credit, CreditPack, Gateway, GatewayUser, PaymentMethod, Card, GatewayCard, CreditOrder, GatewayCreditOrder, PagarmeWebhook


admin.site.register(Credit)
admin.site.register(CreditPack)
admin.site.register(Gateway)
admin.site.register(GatewayUser)
admin.site.register(PaymentMethod)
admin.site.register(Card)
admin.site.register(GatewayCard)
admin.site.register(CreditOrder)
admin.site.register(GatewayCreditOrder)
admin.site.register(PagarmeWebhook)