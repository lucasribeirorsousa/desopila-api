from django.db import models
from checkout.utils import BANKS, BANK_CHOICES


class Gateway(models.Model):
    name = models.CharField(verbose_name='Nome do Gateway', max_length=60, null=False, blank=False, unique=True)
    created = models.DateTimeField(verbose_name='Data de Criação', auto_now_add=True)

    class Meta:
        verbose_name = 'Gateway de Pagamento'
        verbose_name_plural = 'Gateways de Pagamento'

    def __str__(self):
        return f'{self.id}: {self.name}'


class Credit(models.Model):
    user = models.ForeignKey('authentication.User', verbose_name="Cliente", on_delete=models.CASCADE)
    amount = models.DecimalField(verbose_name="Montante", max_digits=10, decimal_places=2, null=False, default=0)
    modified = models.DateTimeField(verbose_name="Data da última modificação", auto_now=True)

    class Meta:
        verbose_name = "Crédito"
        verbose_name_plural = "Créditos"

    def __str__(self):
        return f'{self.user.username}: {self.amount} créditos'


class CreditPack(models.Model):
    STATUS_CHOICES = [
        (1, "activated"),
        (2, "deactivated")
    ]

    name = models.CharField('Nome do pacote de crédito', max_length=30, null=False, blank=False)
    price =  models.DecimalField(verbose_name="Preço unitário", max_digits=10, decimal_places=2, null=False)
    credit_amount = models.DecimalField(verbose_name="Montante de créditos", max_digits=10, decimal_places=2, null=False)
    status = models.PositiveSmallIntegerField(verbose_name='Situação', choices=STATUS_CHOICES, null=False, default=1)
    created = models.DateTimeField(verbose_name="Data da criação", auto_now_add=True)
    modified = models.DateTimeField(verbose_name="Data da última modificação", auto_now=True)

    class Meta:
        verbose_name = "Pacote de crédito"
        verbose_name_plural = "Pacotes de crédito"

    def __str__(self):
        return f'Pacote {self.name}: {self.credit_amount} créditos'


class CreditOrder(models.Model):
    STATUS_CHOICES = [
        (1, 'pending'),     #pendente
        (2, 'completed'),   #concluido
        (3, 'canceled'),    #cancelado
    ]

    user = models.ForeignKey("authentication.User", verbose_name="Usuário", on_delete=models.CASCADE, null=False)
    credit_pack = models.ForeignKey("checkout.CreditPack", verbose_name="Pacote de crédito", on_delete=models.PROTECT, null=False)
    payment_method = models.ForeignKey("checkout.PaymentMethod", verbose_name="Método de pagamento", on_delete=models.PROTECT, null=False)
    card = models.ForeignKey('checkout.Card', verbose_name='Cartão de crédito', on_delete=models.PROTECT, null=True)
    status = models.PositiveSmallIntegerField(verbose_name='Situação', choices=STATUS_CHOICES, null=False, default=1)
    created = models.DateTimeField(verbose_name='Data de entrada', auto_now_add=True)


class GatewayCreditOrder(models.Model):
    gateway = models.ForeignKey('checkout.Gateway', verbose_name='Gateway', on_delete=models.PROTECT)
    credit_order = models.ForeignKey('checkout.CreditOrder', verbose_name='Pedido de crédito', on_delete=models.CASCADE)
    credit_order_on_gateway_id = models.CharField(verbose_name='ID do pedido de crédito no Gateway', max_length=150, null=False)

    class Meta:
        verbose_name = 'Pedido no Gateway'
        verbose_name_plural = 'Pedidos no Gateway'

    def __str__(self):
        return f'{self.id}: {self.credit_order} - {self.gateway}'


class GatewayUser(models.Model):
    gateway = models.ForeignKey('checkout.Gateway', verbose_name='Gateway', on_delete=models.PROTECT)
    user = models.ForeignKey('authentication.User', verbose_name='Usuário', on_delete=models.CASCADE)
    user_on_gateway_id = models.CharField(verbose_name='ID de usuário no Gateway', max_length=128, null=False)
    receiver_id = models.CharField(verbose_name='Conta do usuário no Gateway', max_length=150, null=True)

    class Meta:
        verbose_name = 'Usuário no Gateway'
        verbose_name_plural = 'Usuários no Gateway'

    def __str__(self):
        return f'{self.id}: {self.user} - {self.gateway}'


class PaymentMethod(models.Model):
    METHODS_CHOICES = [
        (1, 'credit'),
        (2, 'debit'),
        (3, 'pix'),
    ]
    method = models.PositiveSmallIntegerField(verbose_name="Método", choices=METHODS_CHOICES, unique=True)
    created = models.DateTimeField(verbose_name='Data de entrada', auto_now_add=True)

    class Meta:
        verbose_name = 'Método de pagamento'
        verbose_name_plural = 'Métodos de pagamento'

    def __str__(self):
        return f'Método de pagamento: {self.id}'


class Card(models.Model):
    user = models.ForeignKey('authentication.User', verbose_name='Usuário', on_delete=models.PROTECT)
    brand = models.CharField(verbose_name='Bandeira', max_length=20, null=False)
    last_digits = models.CharField(verbose_name='4 Últimos dígitos', max_length=4, null=False)
    holder_name = models.CharField(verbose_name='Nome do Titular', max_length=60, null=False)
    billing_address = models.ForeignKey('places.Address', verbose_name='Endereço de cobrança', on_delete=models.CASCADE)
    created = models.DateTimeField(verbose_name='Data de Criação', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Cartão'
        verbose_name_plural = 'Cartões'

    def __str__(self):
        return f'{self.id}: {self.brand} - {self.last_digits} - {self.holder_name}'


class GatewayCard(models.Model):
    gateway = models.ForeignKey('checkout.Gateway', verbose_name='Gateway', on_delete=models.PROTECT)
    card = models.ForeignKey('checkout.Card', verbose_name='Cartão de Crédito', on_delete=models.CASCADE, related_name="gateway_card_set")
    card_on_gateway_id = models.CharField(verbose_name='ID do cartão no Gateway', max_length=150, null=False)

    class Meta:
        verbose_name = 'Cartão de Crédito no Gateway'
        verbose_name_plural = 'Cartões de Crédito no Gateway'

    def __str__(self):
        return f'{self.id}: {self.card} - {self.gateway}'


class PagarmeWebhook(models.Model):
    pagarme_id = models.CharField(verbose_name="Pagarme Webhook ID", max_length=60, null=False)
    description = models.CharField(verbose_name="Descrição", max_length=150, null=False)
    class Meta:
        verbose_name = 'Pagarme Webhook'
        verbose_name_plural = 'Pagarme Webhooks'

    def __str__(self):
        return f'{self.id}: {self.pagarme_id} - {self.description}'