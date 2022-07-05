from django.urls import path

from cim_service.views import index

urlpatterns = [
    path('index/', index)
]