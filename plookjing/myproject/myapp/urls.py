from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'myapp'

urlpatterns = [
    # หน้าหลัก
    path('', views.home, name='home'),

    # เลือกต้นไม้
    path('select-tree/', views.select_tree, name='select_tree'),
    path('tree/<int:tree_id>/', views.tree_detail, name='tree_detail'),


    # แผนการปลูก
    path('planting-plan/', views.planting_plan, name='planting_plan'),

    # ร้านอุปกรณ์
    path('equipment-shop/list/', views.equipment_list, name='equipment_list'),
    path('equipment-shop/list/equipment-detail/', views.equipment_detail, name='equipment_detail'),

    # ต้นไม้ของฉัน
    path('my-trees/', views.my_trees, name='my_trees'),

    # ประวัติการสั่งซื้อ
    path('purchase-history/', views.purchase_history, name='purchase_history'),

    # แจ้งเตือน
    path('notifications/', views.notifications, name='view_notifications'),

    # เกี่ยวกับเรา
    path('about/', views.about, name='about'),

    path('profile/', views.user_profile, name='user_profile'),

]
