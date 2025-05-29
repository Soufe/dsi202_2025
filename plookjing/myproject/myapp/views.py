from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Tree, Equipment


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


# 🧾 เลือกจังหวัดและจำนวนสำหรับต้นไม้ (ชำระเงินทันที)
def tree_order(request, tree_id):
    tree = get_object_or_404(Tree, pk=tree_id)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        province = request.POST.get('province', '')

        request.session['tree_order'] = {
            'id': tree.id,
            'name': tree.name,
            'price': float(tree.price),
            'quantity': quantity,
            'province': province,
        }
        return redirect('myapp:payment')  # 🔁 เปลี่ยนเป็นหน้าชำระเงินจริงที่คุณใช้

    return render(request, 'myapp/tree_order.html', {'tree': tree})

def equipment_list(request):
    query = request.GET.get('q')
    equipments = Equipment.objects.filter(name__icontains=query) if query else Equipment.objects.all()
    return render(request, 'myapp/equipment_list.html', {'equipments': equipments})


# 🛒 เพิ่มสินค้าไปยังตะกร้า
def add_to_cart(request, product_id):
    cart = request.session.get('cart', [])
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += 1
            break
    else:
        cart.append({'id': product_id, 'quantity': 1})
    request.session['cart'] = cart
    return redirect('cart')



# 🛒 แสดงหน้าตะกร้าสินค้า
def cart_view(request):
    cart = request.session.get('cart', [])
    tree_items = []
    equipment_items = []

    for item in cart:
        if item['type'] == 'tree':
            try:
                tree = Tree.objects.get(id=item['id'])
                tree_items.append({
                    'id': tree.id,
                    'name': tree.name,
                    'image': tree.image,
                    'quantity': item['quantity'],
                    'price': getattr(tree, 'price', 0),
                })
            except Tree.DoesNotExist:
                pass
        elif item['type'] == 'equipment':
            try:
                equipment = Equipment.objects.get(id=item['id'])
                equipment_items.append({
                    'id': equipment.id,
                    'name': equipment.name,
                    'image': equipment.image,
                    'quantity': item['quantity'],
                    'price': getattr(equipment, 'price', 0),
                })
            except Equipment.DoesNotExist:
                pass

    context = {
        'tree_items': tree_items,
        'equipment_items': equipment_items,
    }
    return render(request, 'myapp/cart.html', context)


# ❌ ลบรายการออกจากตะกร้า
@require_POST
def update_quantity(request, item_id):
    cart = request.session.get('cart', [])
    item_id = int(item_id)
    cart = [item for item in cart if int(item['id']) != item_id]
    request.session['cart'] = cart
    return redirect('myapp:cart')


# 👤 สมัครสมาชิก
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('myapp:home')
    else:
        form = UserCreationForm()
    return render(request, 'myapp/signup.html', {'form': form})


# 📖 เกี่ยวกับเรา
def about(request):
    return render(request, 'myapp/about.html')


# 👤 โปรไฟล์ผู้ใช้
@login_required
def user_profile(request):
    return render(request, 'myapp/user_profile.html', {'user': request.user})