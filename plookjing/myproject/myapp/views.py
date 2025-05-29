from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .models import Tree, Equipment
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

# ✅ Home
def home(request):
    return render(request, 'myapp/home.html')

# ✅ Select Tree (แสดงรายการต้นไม้)
def select_tree(request):
    query = request.GET.get('q')
    if query:
        trees = Tree.objects.filter(name__icontains=query)
    else:
        trees = Tree.objects.all()
    return render(request, 'myapp/select_tree.html', {'trees': trees})

def choose_species(request):
    return render(request, 'myapp/choose_species.html')

def specify_location(request):
    return render(request, 'myapp/specify_location.html')

# ✅ Planting Plan
def planting_plan(request):
    return render(request, 'myapp/planting_plan.html')

def choose_plan(request):
    return render(request, 'myapp/choose_plan.html')

def set_quantity(request):
    return render(request, 'myapp/set_quantity.html')

def subscribe(request):
    return render(request, 'myapp/subscribe.html')

# ✅ Equipment Shop
def equipment_shop(request):
    return render(request, 'myapp/equipment_shop.html')

from .models import Equipment

def equipment_list(request):
    query = request.GET.get('q')
    if query:
        equipment_list = Equipment.objects.filter(name__icontains=query)
    else:
        equipment_list = Equipment.objects.all()
    return render(request, 'myapp/equipment_list.html', {'equipment_list': equipment_list})

def equipment_detail(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    return render(request, 'myapp/equipment_detail.html', {'equipment': equipment})

def equipment_purchase(request):
    return render(request, 'myapp/purchase_equipment.html')

# ✅ Notifications
def view_care_notifications(request):
    return render(request, 'myapp/view_care_notifications.html')

def notifications(request):
    return render(request, 'view_notifications.html')

# ✅ My Trees
def my_trees(request):
    return render(request, 'myapp/my_trees.html')

def tree_detail(request, tree_id):
    tree = get_object_or_404(Tree, pk=tree_id)
    return render(request, 'myapp/tree_detail.html', {'tree': tree})

def growth_status(request):
    return render(request, 'myapp/growth_status.html')

def care_history(request):
    return render(request, 'myapp/care_history.html')

# ✅ Purchase History
def purchase_history(request):
    return render(request, 'myapp/purchase_history.html')

def view_order(request):
    return render(request, 'myapp/view_order.html')






def add_to_cart(request, item_type, item_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', [])

        # เพิ่มรายการใหม่
        cart.append({
            'type': item_type,
            'id': item_id,
            'quantity': quantity
        })
        request.session['cart'] = cart

    return redirect('myapp:cart')

@require_POST
def buy_now(request, item_type, item_id):
    quantity = int(request.POST.get('quantity', 1))
    request.session['checkout_cart'] = [{
        'id': item_id,
        'type': item_type,
        'quantity': quantity
    }]
    return redirect('myapp:payment')

def cart_view(request):
    cart = request.session.get('cart', [])

    tree_items = []
    equipment_items = []

    for item in cart:
        if item['type'] == 'tree':
            tree = Tree.objects.filter(id=item['id']).first()
            if tree:
                tree_items.append({
                    'id': tree.id,
                    'name': tree.name,
                    'price': tree.price,
                    'image': tree.image,
                    'quantity': item['quantity'],
                })
        elif item['type'] == 'equipment':
            eq = Equipment.objects.filter(id=item['id']).first()
            if eq:
                equipment_items.append({
                    'id': eq.id,
                    'name': eq.name,
                    'price': eq.price,
                    'image': eq.image,
                    'quantity': item['quantity'],
                })

    context = {
        'tree_items': tree_items,
        'equipment_items': equipment_items,
    }
    return render(request, 'cart.html', context)


@require_POST
def update_quantity(request, item_id):
    action = request.POST.get('action')
    cart = request.session.get('cart', [])

    for item in cart:
        if str(item.get('id')) == str(item_id):
            if action == 'increase':
                item['quantity'] += 1
            elif action == 'decrease' and item['quantity'] > 1:
                item['quantity'] -= 1
            break

    request.session['cart'] = cart
    return redirect('myapp:cart')

@require_POST
def checkout_selected(request):
    selected_ids = request.POST.getlist('selected_items')
    cart = request.session.get('cart', [])
    selected_items = [item for item in cart if str(item['id']) in selected_ids]
    request.session['checkout_cart'] = selected_items
    return redirect('myapp:payment')


def tree_order(request, tree_id):
    tree = get_object_or_404(Tree, pk=tree_id)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        province = request.POST.get('province')
        
        # ✅ จำลองการสร้างออเดอร์ → อนาคตอาจ save เข้า DB ได้
        request.session['tree_order'] = {
            'id': tree.id,
            'name': tree.name,
            'price': float(tree.price),
            'quantity': quantity,
            'province': province,
        }
        return redirect('myapp:payment')  # ไปหน้าชำระเงิน
    return render(request, 'myapp/tree_order.html', {'tree': tree})




# ✅ Signup (สามารถปิดการใช้งานได้หากไม่ใช้ระบบผู้ใช้)
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

# ✅ About
def about(request):
    return render(request, 'myapp/about.html')

@login_required
def user_profile(request):
    user = request.user
    return render(request, 'myapp/user_profile.html', {'user': user})