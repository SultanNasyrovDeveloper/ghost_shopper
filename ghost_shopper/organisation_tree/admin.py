from django.contrib import admin
from .models import OrganisationTreeNode


@admin.register(OrganisationTreeNode)
class OrganisationTreeNodeAdmin(admin.ModelAdmin):
    pass
