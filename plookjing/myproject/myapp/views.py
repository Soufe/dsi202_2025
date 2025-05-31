from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Tree, Equipment, Notification, UserPlanting, UserEquipment
from datetime import datetime, date
import stripe
from django.conf import settings
from .promptpay_qr import generate_promptpay_qr_payload
from .promptpay_qr import create_promptpay_qr_base64
import qrcode
import io
import base64
from collections import defaultdict
from django.utils import timezone



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
            return redirect('myapp:home')

        # อัปเดตถ้ามีของเดิมในตะกร้า
        for item in cart:
            if item['id'] == product.id and item['type'] == product_type:
                item['quantity'] += quantity
                break
        else:
            cart.append({
                'id': product.id,
                'type': product_type,
                'name': product.name,
                'image_url': product.image.url if product.image else '',
                'price': float(product.price),
                'quantity': quantity,
                'selected': True,
            })

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('myapp:cart')

# 🛒 แสดงหน้าตะกร้า
@login_required
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
                'price': float(product.price),  # แปลงเป็น float เผื่อคำนวณ
                'quantity': item.get('quantity', 1),
                'image_url': product.image.url if product.image else '',
            }

            if item['type'] == 'tree':
                tree_items.append(item_info)
            else:
                equipment_items.append(item_info)

    total_tree = sum(i['price'] * i['quantity'] for i in tree_items)
    total_equipment = sum(i['price'] * i['quantity'] for i in equipment_items)

    context = {
        'tree_items': tree_items,
        'equipment_items': equipment_items,
        'total_tree': total_tree,
        'total_equipment': total_equipment,
        'total': total_tree + total_equipment,
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

    request.session['payment'] = [{
        'id': product.id,
        'type': product_type,
        'name': product.name,
        'image_url': product.image.url if product.image else '',
        'price': str(product.price),
        'quantity': 1,
        'selected': True,
    }]
    request.session.modified = True

    return redirect('payment')

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

@login_required
def update_cart(request):
    if request.method == 'POST':
        cart = request.session.get('cart', [])
        item_id = int(request.POST.get('item_id'))
        item_type = request.POST.get('item_type')
        action = request.POST.get('action')

        for item in cart:
            if item['id'] == item_id and item['type'] == item_type:
                if action == 'increase':
                    item['quantity'] += 1
                elif action == 'decrease':
                    if item['quantity'] > 1:
                        item['quantity'] -= 1
                break

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('myapp:cart')


# ❌ ลบจากตะกร้า
@login_required
def remove_from_cart(request, item_id):
    item_type = request.POST.get('item_type')
    cart = request.session.get('cart', [])

    # ลบ item ที่ตรงทั้ง id และ type
    cart = [item for item in cart if not (item['id'] == item_id and item['type'] == item_type)]

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

# 🧾 ประวัติการสั่งซื้อ
@login_required
def purchase_history(request):
    purchases = UserEquipment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'myapp/purchase_history.html', {'purchases': purchases})

# 🔔 การแจ้งเตือน
@login_required
def notifications(request):
    alerts = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'myapp/notifications.html', {'alerts': alerts})

# ✅ ยืนยันตำแหน่ง → ไปยัง tree_order
@login_required
def tree_order(request, tree_id):
    cart = request.session.get('cart', [])
    tree_items = []

    for item in cart:
        if item['type'] == 'tree':
            tree = get_object_or_404(Tree, id=item['id'])
            tree_items.append({
                'id': item['id'],
                'name': tree.name,
                'description': tree.description,
                'image_url': tree.image.url if tree.image else '',
                'price': float(tree.price),
                'quantity': item['quantity'],
                'total_price': float(tree.price) * item['quantity']
            })


    provinces = [
        "กรุงเทพมหานคร", "กระบี่", "กาญจนบุรี", "กาฬสินธุ์", "กำแพงเพชร", "ขอนแก่น", "จันทบุรี", "ฉะเชิงเทรา", "ชลบุรี",
        "ชัยนาท", "ชัยภูมิ", "ชุมพร", "เชียงราย", "เชียงใหม่", "ตรัง", "ตราด", "ตาก", "นครนายก", "นครปฐม", "นครพนม",
        "นครราชสีมา", "นครศรีธรรมราช", "นครสวรรค์", "นนทบุรี", "นราธิวาส", "น่าน", "บึงกาฬ", "บุรีรัมย์", "ปทุมธานี",
        "ประจวบคีรีขันธ์", "ปราจีนบุรี", "ปัตตานี", "พระนครศรีอยุธยา", "พะเยา", "พังงา", "พัทลุง", "พิจิตร", "พิษณุโลก",
        "เพชรบุรี", "เพชรบูรณ์", "แพร่", "พังงา", "ภูเก็ต", "มหาสารคาม", "มุกดาหาร", "แม่ฮ่องสอน", "ยโสธร", "ยะลา",
        "ร้อยเอ็ด", "ระนอง", "ระยอง", "ราชบุรี", "ลพบุรี", "ลำปาง", "ลำพูน", "เลย", "ศรีสะเกษ", "สกลนคร", "สงขลา",
        "สตูล", "สมุทรปราการ", "สมุทรสงคราม", "สมุทรสาคร", "สระแก้ว", "สระบุรี", "สิงห์บุรี", "สุโขทัย", "สุพรรณบุรี",
        "สุราษฎร์ธานี", "สุรินทร์", "หนองคาย", "หนองบัวลำภู", "อ่างทอง", "อำนาจเจริญ", "อุดรธานี", "อุตรดิตถ์",
        "อุทัยธานี", "อุบลราชธานี"
    ]

    return render(request, 'myapp/tree_order.html', {
        'tree_items': tree_items,
        'provinces': provinces,
    })

@login_required
def confirm_tree_order(request):
    if request.method == 'POST':
        cart = request.session.get('cart', [])
        tree_cart = []
        
        for item in cart:
            if item.get('type') == 'tree':
                try:
                    tree = Tree.objects.get(id=item['id'])
                    quantity = int(item.get('quantity', 1))
                    price = float(tree.price)
                    total_price = price * quantity
                    province = request.POST.get(f'province_{item["id"]}', '')
                    
                    if not province:
                        continue  # ข้ามถ้ายังไม่เลือกจังหวัด

                    tree_cart.append({
                        'id': tree.id,
                        'name': tree.name,
                        'image_url': tree.image.url if tree.image else '',
                        'quantity': quantity,
                        'price': price,
                        'total_price': total_price,
                        'province': province,
                    })
                except Tree.DoesNotExist:
                    continue

        if not tree_cart:
            return redirect('myapp:tree_order')  # กลับไปถ้าไม่มีข้อมูล

        total = sum(item['total_price'] for item in tree_cart)
        now = timezone.now()
        qr_base64 = create_promptpay_qr_base64("0922894514", total)

        request.session['tree_payment_items'] = tree_cart

        return render(request, 'myapp/payment_tree.html', {
            'items': tree_cart,
            'total': total,
            'qr_base64': qr_base64,
            'order_date': now.strftime("%Y-%m-%d %H:%M"),
            'order_id': f"TREE{now.strftime('%Y%m%d%H%M%S')}",
        })

    return redirect('myapp:tree_order')





# ✅ ยืนยันที่อยู่ → ไปยัง equipment_order
@login_required
def equipment_order(request):
    cart = request.session.get('cart', [])
    equipment_items = []

    for item in cart:
        if item['type'] == 'equipment':
            equipment_items.append({
                'id': item['id'],
                'name': item['name'],
                'image_url': item.get('image_url', ''),
                'price': float(item['price']),
                'quantity': item['quantity'],
                'total_price': float(item['price']) * item['quantity']
            })

    total_equipment = sum(item['total_price'] for item in equipment_items)

    return render(request, 'myapp/equipment_order.html', {
        'equipment_items': equipment_items,
        'total_equipment': total_equipment,
    })



from django.shortcuts import render
from datetime import datetime

@login_required
def payment_tree(request):
    cart = request.session.get('cart', [])
    tree_cart = []

    for item in cart:
        if item.get('type') == 'tree':
            try:
                tree = Tree.objects.get(id=item['id'])
                quantity = int(item.get('quantity', 1))
                price = float(tree.price)
                total_price = price * quantity
                tree_cart.append({
                    'id': tree.id,
                    'name': tree.name,
                    'image_url': tree.image.url if tree.image else '',
                    'quantity': quantity,
                    'price': price,
                    'province': item.get('province', '-'),
                    'total_price': total_price,
                })
            except Tree.DoesNotExist:
                continue

    total = sum(item['total_price'] for item in tree_cart)
    now = datetime.now()
    qr_base64 = create_promptpay_qr_base64("0922894514", total)

    return render(request, 'myapp/payment_tree.html', {
        'items': tree_cart,
        'total': total,
        'qr_base64': qr_base64,
        'order_date': now.strftime("%Y-%m-%d %H:%M"),
        'order_id': f"TREE{now.strftime('%Y%m%d%H%M%S')}",
    })


@login_required
def upload_slip_tree(request):
    if request.method == 'POST' and request.FILES.get('slip'):
        slip = request.FILES['slip']
        # ✅ TODO: บันทึก slip, สร้าง Purchase, หรือ update session/database

        # ✅ redirect ไปหน้า my_trees
        return redirect('myapp:my_trees')

    return redirect('myapp:select_tree')





@login_required
def confirm_payment_tree(request):
    if request.method == 'POST':
        cart = request.session.get('cart', [])
        selected_tree_ids = []
        province_map = {}

        for key in request.POST:
            if key.startswith('tree_ids_'):
                tree_id = request.POST[key]
                province = request.POST.get(f'province_{tree_id}')
                if province:
                    selected_tree_ids.append(tree_id)
                    province_map[tree_id] = province

        request.session['selected_tree_ids'] = selected_tree_ids
        request.session['province_map'] = province_map

        return redirect('myapp:payment_tree')






@login_required
def my_trees(request):
    plantings = UserPlanting.objects.filter(user=request.user)

    # ✅ แปลงสถานะให้แสดงชื่อไทย
    STATUS_DISPLAY = {
        'pending': 'รอดำเนินการ',
        'planted': 'ปลูกแล้ว',
        'growing': 'กำลังเติบโต',
        'completed': 'ปลูกเสร็จสิ้น',
    }

    # ✅ รวมรายการที่ซ้ำกันตาม tree + status
    grouped = defaultdict(lambda: {
        'quantity': 0,
        'locations': set(),
        'planted_date': None,
        'tree': None,
        'status': None
    })

    for p in plantings:
        key = (p.tree.id, p.status)
        grouped[key]['quantity'] += getattr(p, 'quantity', 1)
        grouped[key]['locations'].add(p.location_name)
        grouped[key]['planted_date'] = p.planted_date
        grouped[key]['tree'] = p.tree
        grouped[key]['status'] = p.status

    # ✅ แปลงให้อยู่ในรูปแบบที่ template ใช้งานได้
    grouped_plantings = [{
        'tree': v['tree'],
        'status': v['status'],
        'status_display': STATUS_DISPLAY.get(v['status'], v['status']),
        'quantity': v['quantity'],
        'location': ", ".join(v['locations']),
        'planted_date': v['planted_date']
    } for v in grouped.values()]

    # ✅ เรียงตามวันที่ปลูกใหม่ล่าสุด
    grouped_plantings.sort(key=lambda x: x['planted_date'], reverse=True)

    return render(request, 'myapp/my_trees.html', {
        'plantings': grouped_plantings,
    })















@login_required
def payment_equipment(request):
    if request.method == 'POST' and request.FILES.get('slip'):
        slip = request.FILES['slip']
        cart = request.session.get('checkout_cart', [])
        order_info = request.session.get('order_info', {})

        for item in cart:
            if item['type'] == 'equipment':
                UserEquipment.objects.create(
                    user=request.user,
                    equipment_id=item['id'],
                    quantity=item['quantity'],
                    address=order_info.get('address', ''),
                    tel=order_info.get('tel', ''),
                    payment_slip=slip,
                    status='pending',  # ✅ default after payment
                )

        # ✅ Clear session cart
        request.session['checkout_cart'] = []

        return redirect('myapp:my_orders')  # ✅ ลิงก์ไปหน้าแสดงรายการ
    return redirect('myapp:equipment_list')



@login_required
def upload_slip_equipment(request):
    if request.method == 'POST' and request.FILES.get('slip'):
        slip = request.FILES['slip']
        # TODO: บันทึก slip กับคำสั่งซื้อ (ควรใช้ session หรือ DB)
        # ตัวอย่าง: save_to_model_or_session(request.user, slip)

        # 🔁 แนะนำ redirect ไปหน้า my_orders หรือหน้าสรุปผล
        return redirect('myapp:my_orders')
    return redirect('home')  # fallback ถ้าไม่ใช่ POST






@login_required
def my_orders(request):
    all_orders = UserEquipment.objects.filter(
        user=request.user,
        payment_slip__isnull=False  # ✅ เฉพาะที่จ่ายเงินแล้ว (แนบสลิปแล้ว)
    ).order_by('-created_at')

    status_filter = request.GET.get('status', 'ทั้งหมด')
    if status_filter != 'ทั้งหมด':
        filtered_orders = all_orders.filter(status=status_filter)
    else:
        filtered_orders = all_orders

    status_choices = [choice[0] for choice in UserEquipment.STATUS_CHOICES]
    status_choices.insert(0, 'ทั้งหมด')

    return render(request, 'myapp/my_orders.html', {
        'orders': filtered_orders,
        'selected_status': status_filter,
        'status_choices': status_choices,
    })






def create_promptpay_qr_base64(mobile, amount):
    payload = generate_promptpay_qr_payload(mobile=mobile, amount=amount, one_time=True)
    qr = qrcode.make(payload)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return qr_base64


