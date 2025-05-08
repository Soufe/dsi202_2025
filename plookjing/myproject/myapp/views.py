from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Tree, Equipment, PlantingLocation, UserPlanting, Notification, NewsArticle  # อย่าลืม import

def home(request):
    return render(request, 'myapp/home.html')

def tree_list(request):
    sort = request.GET.get('sort')
    if sort:
        trees = Tree.objects.all().order_by(sort)
    else:
        trees = Tree.objects.all()

    recommended_trees = Tree.objects.order_by('?')[:3]
    return render(request, 'myapp/tree_list.html', {
        'trees': trees,
        'recommended_trees': recommended_trees
    })

def tree_detail(request, tree_id):
    tree = get_object_or_404(Tree, id=tree_id)
    return render(request, 'myapp/tree_detail.html', {'tree': tree})

def equipment_list(request):
    equipments = Equipment.objects.all()
    return render(request, 'myapp/equipment_list.html', {'equipments': equipments})

def equipment_detail(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    return render(request, 'myapp/equipment_detail.html', {'equipment': equipment})

@login_required
def purchase_equipment(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    Purchase.objects.create(
        user=request.user,
        equipment=equipment,
        quantity=1,
        purchase_date=timezone.now()
    )
    Notification.objects.create(
        user=request.user,
        message=f'คุณได้ซื้อ {equipment.name} แล้ว',
        notification_date=timezone.now(),
        is_read=False
    )
    return redirect('notification_list')

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-notification_date')
    return render(request, 'myapp/notification_list.html', {'notifications': notifications})

@login_required
def plant_tree(request, tree_id):
    tree = get_object_or_404(Tree, id=tree_id)
    UserPlanting.objects.create(
        user=request.user,
        tree=tree,
        location=None,
        planting_date=timezone.now(),
        is_completed=True
    )
    Notification.objects.create(
        user=request.user,
        message=f'คุณได้ปลูก {tree.name} แล้ว!',
        notification_date=timezone.now(),
        is_read=False
    )
    return redirect('notification_list')


@login_required
def plant_tree_at_location(request):
    if request.method == 'POST':
        tree_id = request.POST.get('tree_id')
        location_id = request.POST.get('location_id')
        tree = get_object_or_404(Tree, id=tree_id)
        location = get_object_or_404(PlantingLocation, id=location_id)
        UserPlanting.objects.create(
            user=request.user,
            tree=tree,
            location=location,
            planting_date=timezone.now(),
            is_completed=True
        )
        Notification.objects.create(
            user=request.user,
            message=f'คุณได้ปลูก {tree.name} ที่ {location.name} แล้ว!',
            notification_date=timezone.now(),
            is_read=False
        )
        return redirect('notification_list')

@login_required
def payment(request, tree_id):
    tree = get_object_or_404(Tree, id=tree_id)
    return render(request, 'myapp/payment.html', {'tree': tree})

@login_required
def my_trees(request):
    planted = UserPlanting.objects.filter(user=request.user).order_by('-planting_date')
    return render(request, 'myapp/my_trees.html', {'planted_trees': planted})

@login_required
def user_profile(request):
    return render(request, 'myapp/user_profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = UserChangeForm(instance=request.user)

    return render(request, 'myapp/edit_profile.html', {'form': form})

from .models import NewsArticle  # อย่าลืม import

def news_list(request):
    news = NewsArticle.objects.all().order_by('-published_date')  # เรียงข่าวใหม่สุดก่อน
    return render(request, 'myapp/news_list.html', {'news': news})

def search_results(request):
    query = request.GET.get('q')
    trees = Tree.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    equipments = Equipment.objects.filter(Q(name__icontains=query))
    news = NewsArticle.objects.filter(Q(title__icontains=query))

    return render(request, 'myapp/search_results.html', {
        'query': query,
        'trees': trees,
        'equipments': equipments,
        'news': news,
    })

def community(request):
    return render(request, 'myapp/community.html')

def about(request):
    return render(request, 'myapp/about.html')

@login_required
def select_location_for_tree(request, tree_id):
    tree = get_object_or_404(Tree, id=tree_id)
    locations = PlantingLocation.objects.all()
    return render(request, 'myapp/select_location_for_tree.html', {
        'tree': tree,
        'locations': locations
    })

@login_required
def plant_tree(request, tree_id):
    tree = get_object_or_404(Tree, id=tree_id)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))

        # ปลูกตามจำนวน
        for _ in range(quantity):
            UserPlanting.objects.create(
                user=request.user,
                tree=tree,
                planting_date=timezone.now(),
                is_completed=True
            )

        Notification.objects.create(
            user=request.user,
            message=f"คุณได้ปลูกต้นไม้ {tree.name} จำนวน {quantity} ต้นแล้ว!",
            notification_date=timezone.now(),
            is_read=False
        )

        return redirect('user_profile')

    return redirect('tree_detail', tree_id=tree_id)


def home(request):
    news_list = NewsArticle.objects.all().order_by('-created_at')[:5]  # เอาข่าวใหม่สุด
    return render(request, 'myapp/home.html', {'news_list': news_list})