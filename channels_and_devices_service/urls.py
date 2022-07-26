from django.urls import path


from .views import api_nodes, api_node_detail, api_nodes_by_device, api_create_beam, api_create_branch, \
    api_table_for_device, api_route_by_node

urlpatterns = [
    path('api/nodes/', api_nodes),
    path('api/nodes/<uuid:id>', api_node_detail),
    path('api/nodes_by_device/<uuid:device_id>', api_nodes_by_device),
    path('api/create_beam/', api_create_beam),
    path('api/create_branch/', api_create_branch),
    path('api/table_by_device/<uuid:device_id>', api_table_for_device),
    path('api/route_by_node/<uuid:node_id>', api_route_by_node)
]