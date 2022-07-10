from django.urls import path

from .views import api_substations, api_substation_detail, api_companies, api_permissions

urlpatterns = [
    path('api/substations/', api_substations),
    path('api/substations/<uuid:id>/', api_substation_detail),
    path('api/companies/', api_companies),
    path('api/companies/<uuid:id>/', api_substation_detail),
    path('api/permissions/', api_permissions),
]