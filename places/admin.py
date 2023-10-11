from django.contrib import admin
from .models import Address, WeekDay, PlaceAds, Plan

# Register your models here.
admin.site.register(Address)
admin.site.register(WeekDay)
admin.site.register(PlaceAds)
admin.site.register(Plan)
