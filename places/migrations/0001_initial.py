# Generated by Django 3.1.5 on 2021-10-12 13:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('asset', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('map_string', models.CharField(max_length=200, verbose_name='Logradouro')),
                ('reference', models.CharField(max_length=60, verbose_name='Ponto de Referência')),
                ('latitude', models.CharField(max_length=50, null=True, verbose_name='Latitude')),
                ('longitude', models.CharField(max_length=50, null=True, verbose_name='Longitude')),
            ],
            options={
                'verbose_name': 'Endereço',
                'verbose_name_plural': 'Endereços',
            },
        ),
        migrations.CreateModel(
            name='Date',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Data')),
            ],
            options={
                'verbose_name': 'Data',
                'verbose_name_plural': 'Datas',
            },
        ),
        migrations.CreateModel(
            name='Days',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.PositiveSmallIntegerField(choices=[(0, 'sunday'), (1, 'monday'), (2, 'tuesday'), (3, 'wednesday'), (4, 'thursday'), (5, 'friday'), (6, 'saturday')], unique=True, verbose_name='Dia da semana')),
            ],
            options={
                'verbose_name': 'Dia da Semana',
                'verbose_name_plural': 'Dias da Semana',
            },
        ),
        migrations.CreateModel(
            name='PlaceAds',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='Nome do local')),
                ('ads_description', models.CharField(max_length=200, verbose_name='Descrição do anúncio')),
                ('place_description', models.CharField(max_length=400, verbose_name='Descrição do local')),
                ('local_type', models.PositiveSmallIntegerField(choices=[(1, 'Chácara'), (2, 'Fazenda'), (3, 'Galpão'), (4, 'Flutuante')], verbose_name='Tipo de Local')),
                ('capacity', models.PositiveSmallIntegerField(choices=[(1, 'Menos de 5 pessoas'), (2, 'Até 10 pessoas'), (3, 'Até 20 pessoas'), (4, 'Até 50 pessoas'), (5, 'Até 100 pessoas')], verbose_name='Capacidade')),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'open'), (2, 'closed')], verbose_name='Status')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='places.address', verbose_name='Endereço')),
                ('images', models.ManyToManyField(to='asset.Asset')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Dono')),
                ('week_days', models.ManyToManyField(to='places.Days')),
            ],
            options={
                'verbose_name': 'Anúncio de local',
                'verbose_name_plural': 'Anúncios de locais',
            },
        ),
    ]
