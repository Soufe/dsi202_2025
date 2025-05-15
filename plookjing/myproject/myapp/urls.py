from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('select-tree/', views.select_tree, name='select_tree'),
    path('select-tree/choose-species/', views.choose_species, name='choose_species'),
    path('select-tree/choose-species/specify-location/', views.specify_location, name='specify_location'),

    path('planting-plan/', views.planting_plan, name='planting_plan'),
    path('planting-plan/choose-plan/', views.choose_plan, name='choose_plan'),
    path('planting-plan/choose-plan/set-quantity/', views.set_quantity, name='set_quantity'),
    path('planting-plan/choose-plan/subscribe/', views.subscribe, name='subscribe'),

    path('equipment-shop/', views.equipment_shop, name='equipment_shop'),
    path('equipment-shop/list/', views.equipment_list, name='equipment_list'),
    path('equipment-shop/list/equipment-detail/', views.equipment_detail, name='equipment_detail'),
    path('equipment-shop/list/purchase/', views.equipment_purchase, name='equipment_purchase'),

    path('notifications/', views.notifications, name='notifications'),
    path('notifications/view-care-notifications/', views.view_care_notifications, name='view_care_notifications'),

    path('my-trees/', views.my_trees, name='my_trees'),
    path('my-trees/tree-detail/', views.tree_detail, name='tree_detail'),
    path('my-trees/tree-detail/growth-status/', views.growth_status, name='growth_status'),
    path('my-trees/tree-detail/care-history/', views.care_history, name='care_history'),

    path('purchase-history/', views.purchase_history, name='purchase_history'),
    path('purchase-history/view-order/', views.view_order, name='view_order'),
]
