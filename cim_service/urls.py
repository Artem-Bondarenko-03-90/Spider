from django.urls import path

from .views import api_substations, api_substation_detail, api_companies, api_permissions, \
    api_permissions_by_company_for_substations

urlpatterns = [
    path('api/substations/', api_substations),
    path('api/substations/<uuid:id>/', api_substation_detail),
    path('api/companies/', api_companies),
    path('api/companies/<uuid:id>/', api_substation_detail),
    path('api/permissions/', api_permissions),
    path('api/permissions_by_company_for_substation/<uuid:company_id>/', api_permissions_by_company_for_substations),
]