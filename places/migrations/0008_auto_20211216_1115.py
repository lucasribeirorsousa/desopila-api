# Generated by Django 3.1.5 on 2021-12-16 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0007_auto_20211128_1124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weekday',
            name='day',
            field=models.PositiveSmallIntegerField(choices=[(0, 'monday'), (1, 'tuesday'), (2, 'wednesday'), (3, 'thursday'), (4, 'friday'), (5, 'saturday'), (6, 'sunday')], unique=True, verbose_name='Dia da semana'),
        ),
    ]
