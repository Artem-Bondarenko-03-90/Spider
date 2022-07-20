from django.urls import path

from .views import api_substations, api_substation_detail, api_companies, api_permissions, \
    api_permissions_by_company_for_substations, api_devices, api_device_detail, api_devices_by_substation

urlpatterns = [
    path('api/substations/', api_substations),
    path('api/substations/<uuid:id>/', api_substation_detail),
    path('api/companies/', api_companies),
    path('api/companies/<uuid:id>/', api_substation_detail),
    path('api/permissions/', api_permissions),
    path('api/permissions_by_company_for_substation/<uuid:company_id>/', api_permissions_by_company_for_substations),
    path('api/devices/', api_devices),
    path('api/devices/<uuid:id>/', api_device_detail),
    path('api/devices_by_substation/<uuid:substation_id>', api_devices_by_substation),
]