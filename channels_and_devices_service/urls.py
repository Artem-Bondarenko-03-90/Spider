from django.urls import path

from channels_and_devices_service.views import index

urlpatterns = [
    path('index/', index)
]