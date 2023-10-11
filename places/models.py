from django.db import models
from django.db.models.aggregates import Avg
from review.models import PlaceRatings

# Create your models here.

class Address(models.Model):
    map_string = models.CharField(verbose_name="Logradouro", max_length=200, null=False, blank=False)
    reference = models.CharField(verbose_name="Ponto de Referência", max_length=60, null=False, blank=False)
    cep = models.CharField(verbose_name="CEP", max_length=8, null=False, blank=False)
    latitude = models.FloatField('Latitude', max_length=50, null=True)
    longitude = models.FloatField('Longitude', max_length=50, null=True)

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"

    def __str__(self):
        return f'{self.id}: {self.map_string} - {self.reference}'


class WeekDay(models.Model):
    class Days(models.IntegerChoices):
        MONDAY = 1, "monday"
        TUESDAY = 2, "tuesday"
        WEDNESDAY = 3, "wednesday"
        THURSDAY = 4, "thursday"
        FRIDAY = 5, "friday"
        SATURDAY = 6, "saturday"
        SUNDAY = 7, "sunday"

    day = models.PositiveSmallIntegerField(
        verbose_name="Dia da semana",
        null=False,
        choices=Days.choices,
        unique=True,
    )

    class Meta:
        verbose_name = "Dia da Semana"
        verbose_name_plural = "Dias da Semana"


class PlaceAds(models.Model):
    LOCAL = [
        (1, 'Casas'),
        (2, 'Chácaras'),
        (3, 'Embarcações'),
        (4, 'Passeios'),
    ]
    
    STATUS = [
        (1, 'open'),
        (2, 'closed'),
    ]
    user = models.ForeignKey('authentication.User', verbose_name="Dono", null=False, on_delete=models.PROTECT)
    address = models.ForeignKey('places.Address', verbose_name="Endereço", null=False, on_delete=models.PROTECT)
    images = models.ManyToManyField('asset.Asset')
    place_title = models.CharField(verbose_name='Título do anúncio', max_length=200, null=False)
    place_description = models.CharField(verbose_name='Descrição do local', max_length=400, null=False)
    local_type = models.PositiveSmallIntegerField(verbose_name="Tipo de Local", choices=LOCAL, null=False)
    capacity = models.PositiveSmallIntegerField(verbose_name="Capacidade", null=False)
    status = models.PositiveSmallIntegerField(verbose_name="Status", choices=STATUS, null=False, default=1)
    created_at = models.DateTimeField(verbose_name="Data de criação", auto_now_add=True)

    @property
    def score(self):
        return PlaceRatings.objects.filter(place=self).aggregate(Avg('rating'))
        
    class Meta:
        verbose_name = "Anúncio de local"
        verbose_name_plural = "Anúncios de locais"

    def __str__(self):
        return f'{self.id}: {self.LOCAL[self.local_type - 1][1]} - {self.place_title}'

    
class Plan(models.Model):
    PLAN_TYPE = [
        (1, 'daily'),
        (2, 'package')
    ]

    place_ads = models.ForeignKey('places.PlaceAds', verbose_name="Anúncio de local", null=False, on_delete=models.PROTECT)
    week_days = models.ManyToManyField('places.WeekDay', verbose_name="Dias da semana")
    plan_type = models.PositiveSmallIntegerField(verbose_name="Tipo de plano", null=False, choices=PLAN_TYPE)
    name = models.CharField(verbose_name="Nome", max_length=45, null=False)
    price = models.FloatField(verbose_name="Preço", null=False)
    created_at = models.DateTimeField(verbose_name="Data de criação", auto_now_add=True)


    class Meta:
        verbose_name = "Plano"
        verbose_name_plural = "Planos"

    def __str__(self):
        return f'{self.id}: {self.PLAN_TYPE[self.plan_type - 1][1]} - {self.name}'

