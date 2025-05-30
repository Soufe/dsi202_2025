from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'myapp'

urlpatterns = [
    # 🏠 หน้าหลัก
    path('', views.home, name='home'),

    # 🌳 เลือกต้นไม้
    path('select-tree/', views.select_tree, name='select_tree'),
    path('tree/<int:tree_id>/', views.tree_detail, name='tree_detail'),
    path('tree/order/<int:tree_id>/', views.tree_order, name='tree_order'),


    # 📦 แผนการปลูก
    path('planting-plan/', views.planting_plan, name='planting_plan'),

    # 🛠️ ร้านอุปกรณ์
    path('equipment-list/', views.equipment_list, name='equipment_list'),
    path('equipment/<int:equipment_id>/', views.equipment_detail, name='equipment_detail'),
    path('equipment-order/', views.equipment_order, name='equipment_order'),
    

    # 🧾 ประวัติการสั่งซื้อ
    path('purchase-history/', views.purchase_history, name='purchase_history'),

    # 🔔 แจ้งเตือน
    path('notifications/', views.notifications, name='view_notifications'),

    # 👤 โปรไฟล์ & เกี่ยวกับเรา
    path('about/', views.about, name='about'),
    path('profile/', views.user_profile, name='user_profile'),

    # 🛒 ตะกร้า
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<str:product_type>/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('buy-now/<str:product_type>/<int:product_id>/', views.buy_now, name='buy_now'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_selected, name='checkout_selected'),

    path('tree/payment/', views.payment_tree, name='payment_tree'),
    path('equipment/payment/', views.payment_equipment, name='payment_equipment'),

    path('upload-slip-tree/', views.upload_slip_tree, name='upload_slip_tree'),
    path('upload-slip-equipment/', views.upload_slip_equipment, name='upload_slip_equipment'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('my-trees/', views.my_trees, name='my_trees'),

]