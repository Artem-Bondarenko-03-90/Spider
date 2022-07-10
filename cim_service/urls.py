from django.urls import path

from .views import api_substations, api_substation_detail

urlpatterns = [
    path('api/substations/', api_substations),
    path('api/substations/<uuid:id>/', api_substation_detail),
]