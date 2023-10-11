# Generated by Django 3.1.5 on 2023-04-12 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0009_address_cep'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weekday',
            name='day',
            field=models.PositiveSmallIntegerField(choices=[(1, 'monday'), (2, 'tuesday'), (3, 'wednesday'), (4, 'thursday'), (5, 'friday'), (6, 'saturday'), (7, 'sunday')], unique=True, verbose_name='Dia da semana'),
        ),
    ]