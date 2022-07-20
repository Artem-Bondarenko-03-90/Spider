from django.urls import path


from .views import api_nodes, api_node_detail, api_nodes_by_device

urlpatterns = [
    path('api/nodes/', api_nodes),
    path('api/nodes/<uuid:id>', api_node_detail),
    path('api/nodes_by_device/<uuid:device_id>', api_nodes_by_device),
]