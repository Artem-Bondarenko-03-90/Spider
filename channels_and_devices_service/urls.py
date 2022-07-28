from django.urls import path


from .views import api_nodes, api_node_detail, api_nodes_by_device, api_create_beam, api_create_branch, \
    api_table_for_device, api_route_by_node, api_selectors, api_selectors_by_device, api_selector_detail, api_positions, \
    api_position_detail, api_connect_position_branch, api_activate_position

urlpatterns = [
    path('api/nodes/', api_nodes),
    path('api/nodes/<uuid:id>', api_node_detail),
    path('api/nodes_by_device/<uuid:device_id>', api_nodes_by_device),
    path('api/create_beam/', api_create_beam),
    path('api/create_branch/', api_create_branch),
    path('api/table_by_device/<uuid:device_id>', api_table_for_device),
    path('api/route_by_node/<uuid:node_id>', api_route_by_node),
    path('api/selectors/', api_selectors),
    path('api/selectors_by_device/<uuid:device_id>', api_selectors_by_device),
    path('api/selectors/<uuid:id>', api_selector_detail),
    path('api/positions/', api_positions),
    path('api/positions/<uuid:id>', api_position_detail),
    path('api/connect_position_branch/', api_connect_position_branch),
    path('api/activate_position/<uuid:position_id>', api_activate_position)
]