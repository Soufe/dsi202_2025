from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Tree, Equipment, Notification, Purchase, UserPlanting

# 🏠 หน้าแรก
def home(request):
    return render(request, 'myapp/home.html')

# 🌳 รายการต้นไม้
def select_tree(request):
    query = request.GET.get('q')
    trees = Tree.objects.filter(name__icontains=query) if query else Tree.objects.all()
    return render(request, 'myapp/select_tree.html', {'trees': trees})

def planting_plan(request):
    return render(request, 'myapp/planting_plan.html')

# 🌳 รายละเอียดต้นไม้
def tree_detail(request, tree_id):
    tree = get_object_or_404(Tree, pk=tree_id)
    return render(request, 'myapp/tree_detail.html', {'tree': tree})

# 🧾 รายการอุปกรณ์
def equipment_list(request):
    query = request.GET.get('q')
    equipments = Equipment.objects.filter(name__icontains=query) if query else Equipment.objects.all()
    return render(request, 'myapp/equipment_list.html', {'equipments': equipments})

def equipment_detail(request, equipment_id):
    equipment = get_object_or_404(Equipment, pk=equipment_id)
    return render(request, 'myapp/equipment_detail.html', {'equipment': equipment})

# 🛒 เพิ่มสินค้าลงตะกร้า
def add_to_cart(request, product_type, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', [])
        quantity = int(request.POST.get('quantity', 1))

        if product_type == 'tree':
            product = get_object_or_404(Tree, pk=product_id)
        elif product_type == 'equipment':
            product = get_object_or_404(Equipment, pk=product_id)
        else:
            return redirect('home')

        cart.append({
            'id': product.id,
            'type': product_type,
            'name': product.name,
            'image_url': product.image.url if product.image else '',
            'price': str(product.price),
            'quantity': quantity,
            'selected': True,
        })
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart')

# 🛒 แสดงตะกร้า
def cart_view(request):
    cart = request.session.get('cart', [])

    tree_items = []
    equipment_items = []

    for item in cart:
        product = None
        if item['type'] == 'tree':
            product = get_object_or_404(Tree, id=item['id'])
        elif item['type'] == 'equipment':
            product = get_object_or_404(Equipment, id=item['id'])

        if product:
            item_info = {
                'id': item['id'],
                'type': item['type'],
                'name': product.name,
                'price': product.price,
                'quantity': item.get('quantity', 1),
                'image_url': product.image.url if product.image else '',
            }

            if item['type'] == 'tree':
                tree_items.append(item_info)
            else:
                equipment_items.append(item_info)

    context = {
        'cart': tree_items + equipment_items,  # ✅ ส่งตัวแปร cart เข้า template
        'total': sum(i['price'] * i['quantity'] for i in tree_items + equipment_items),
    }
    return render(request, 'myapp/cart.html', context)


# ✅ ซื้อทันที (ใช้แทนตะกร้า)
def buy_now(request, product_type, product_id):
    if product_type == 'tree':
        product = get_object_or_404(Tree, pk=product_id)
    elif product_type == 'equipment':
        product = get_object_or_404(Equipment, pk=product_id)
    else:
        return redirect('home')

    request.session['checkout_cart'] = [{
        'id': product.id,
        'type': product_type,
        'name': product.name,
        'image_url': product.image.url if product.image else '',
        'price': str(product.price),
        'quantity': 1,
        'selected': True,
    }]
    request.session.modified = True

    return redirect('checkout_selected')

# 🔁 เช็คเอาท์เฉพาะสินค้าที่เลือก
@login_required
def checkout_selected(request):
    cart = request.session.get('checkout_cart', [])
    selected_items = [item for item in cart if item.get('selected')]
    total = sum(float(item['price']) * item['quantity'] for item in selected_items)

    return render(request, 'myapp/checkout.html', {
        'items': selected_items,
        'total': total
    })

# เพิ่มสินค้า
@require_POST
def update_cart(request):
    cart = request.session.get('cart', [])
    item_id = int(request.POST.get('item_id'))
    new_quantity = int(request.POST.get('quantity'))

    for item in cart:
        if item['id'] == item_id:
            item['quantity'] = new_quantity
            break

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('myapp:cart')

# ❌ ลบจากตะกร้า
@require_POST
def remove_from_cart(request, item_id):
    product_type = request.POST.get('type')
    cart = request.session.get('cart', [])

    # ลบเฉพาะรายการที่ตรง id และ type
    cart = [item for item in cart if not (int(item['id']) == item_id and item['type'] == product_type)]

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('myapp:cart')

# 👤 สมัครสมาชิก
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'myapp/signup.html', {'form': form})

# 📖 เกี่ยวกับเรา
def about(request):
    return render(request, 'myapp/about.html')

# 👤 โปรไฟล์
@login_required
def user_profile(request):
    return render(request, 'myapp/user_profile.html', {'user': request.user})

# 🌱 ต้นไม้ของฉัน
@login_required
def my_trees(request):
    trees = UserPlanting.objects.filter(user=request.user)
    return render(request, 'myapp/mytree.html', {'trees': trees})

# 🧾 ประวัติการสั่งซื้อ
@login_required
def purchase_history(request):
    purchases = Purchase.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'myapp/purchase_history.html', {'purchases': purchases})

# 🔔 การแจ้งเตือน
@login_required
def notifications(request):
    alerts = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'myapp/notifications.html', {'alerts': alerts})

def tree_order(request, tree_id):
    tree = get_object_or_404(Tree, pk=tree_id)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        province = request.POST.get('province', '')

        request.session['checkout_cart'] = [{
            'id': tree.id,
            'type': 'tree',
            'name': tree.name,
            'image_url': tree.image.url if tree.image else '',
            'price': str(tree.price),
            'quantity': quantity,
            'province': province,
            'selected': True,
        }]
        request.session.modified = True
        return redirect('checkout_selected')

    return render(request, 'myapp/tree_order.html', {'tree': tree})