from django.db import models
from django.contrib.auth.models import User

# -------------------- ต้นไม้ --------------------
class Tree(models.Model):
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=100, default="Unknown")
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='tree/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.species})"

# -------------------- แผนการปลูก --------------------
class PlantingPlan(models.Model):
    PLAN_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan_type = models.CharField(max_length=50, choices=PLAN_CHOICES)
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    subscribed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.plan_type} ({self.tree.name})"

# -------------------- อุปกรณ์ --------------------
class Equipment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default="No description")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='equipment_images/', null=True, blank=True)

    def __str__(self):
        return self.name

# -------------------- การสั่งซื้ออุปกรณ์ --------------------
class EquipmentOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.equipment.name} x {self.quantity}"

# -------------------- การปลูกต้นไม้ --------------------
class UserTree(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    planted_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.tree.name}"

# -------------------- การดูแลต้นไม้ --------------------
class TreeCare(models.Model):
    user_tree = models.ForeignKey(UserTree, on_delete=models.CASCADE)
    care_type = models.CharField(max_length=100)  # e.g., Watering, Fertilizing
    care_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user_tree.tree.name} - {self.care_type} on {self.care_date}"

# -------------------- การแจ้งเตือน --------------------
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"To {self.user.username}: {self.message}"