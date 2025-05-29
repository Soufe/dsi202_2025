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

    # 🌿 ต้นไม้ของฉัน
    path('my-trees/', views.my_trees, name='my_trees'),

    # 🧾 ประวัติการสั่งซื้อ
    path('purchase-history/', views.purchase_history, name='purchase_history'),

    # 🔔 แจ้งเตือน
    path('notifications/', views.notifications, name='view_notifications'),

    # 👤 โปรไฟล์ & เกี่ยวกับเรา
    path('about/', views.about, name='about'),
    path('profile/', views.user_profile, name='user_profile'),

    # 🛒 ตะกร้า
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<str:item_type>/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_quantity, name='update_quantity'),
    path('cart/checkout-selected/', views.checkout_selected, name='checkout_selected'),

    # 💳 สั่งซื้อทันที
    path('buy-now/<int:item_id>/', views.buy_now, name='buy_now'),
]