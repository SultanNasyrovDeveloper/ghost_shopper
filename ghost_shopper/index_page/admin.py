from django.contrib import admin
from . import models


@admin.register(models.IndexPage)
class IndexPageAdmin(admin.ModelAdmin):
    pass
