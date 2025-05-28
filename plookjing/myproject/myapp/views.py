from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# Home
def home(request):
    return render(request, 'myapp/home.html')

# Select Tree
def select_tree(request):
    return render(request, 'myapp/select_tree.html')

def choose_species(request):
    return render(request, 'myapp/choose_species.html')

def specify_location(request):
    return render(request, 'myapp/specify_location.html')

# Planting Plan
def planting_plan(request):
    return render(request, 'myapp/planting_plan.html')

def choose_plan(request):
    return render(request, 'myapp/choose_plan.html')

def set_quantity(request):
    return render(request, 'myapp/set_quantity.html')

def subscribe(request):
    return render(request, 'myapp/subscribe.html')

# Equipment Shop
def equipment_shop(request):
    return render(request, 'myapp/equipment_shop.html')

def equipment_list(request):
    return render(request, 'myapp/equipment_list.html')

def equipment_detail(request):
    return render(request, 'myapp/equipment_detail.html')

def equipment_purchase(request):
    return render(request, 'myapp/purchase_equipment.html')

# Notifications
def view_care_notifications(request):
    return render(request, 'myapp/view_care_notifications.html')

def notifications(request):
    return render(request, 'notifications.html')

# My Trees
def my_trees(request):
    return render(request, 'myapp/my_trees.html')

def tree_detail(request):
    return render(request, 'myapp/tree_detail.html')

def growth_status(request):
    return render(request, 'myapp/growth_status.html')

def care_history(request):
    return render(request, 'myapp/care_history.html')

# Purchase History
def purchase_history(request):
    return render(request, 'myapp/purchase_history.html')

def view_order(request):
    return render(request, 'myapp/view_order.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
