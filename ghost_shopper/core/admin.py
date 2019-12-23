from django.contrib import admin
from .models import City, CarBrand, CarModel


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass


@admin.register(CarBrand)
class CarBrandAdmin(admin.ModelAdmin):
    pass


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    pass
