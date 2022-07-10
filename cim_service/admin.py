from django.contrib import admin
from .models import Substation, Company
# Register your models here.

class SubstationAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_station']
    list_display_links = ['name']
    search_fields = ['name']

class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ['name']
    search_fields = ['name']

admin.site.register(Substation, SubstationAdmin)
admin.site.register(Company, CompanyAdmin)
