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
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='equipment/', blank=True, null=True)

    def __str__(self):
        return self.name

# -------------------- การสั่งซื้ออุปกรณ์ (เก่า - ยังใช้ได้ถ้าต้องแยก) --------------------
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
    STATUS_CHOICES = [
        ('in_progress', 'กำลังดำเนินการ'),
        ('completed', 'ปลูกเสร็จแล้ว'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    planted_date = models.DateField(auto_now_add=True)

    # ✅ เพิ่ม 2 field ด้านล่างนี้
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    updated_at = models.DateTimeField(auto_now=True)

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



    

class UserPlanting(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('planted', 'Planted'),
        ('growing', 'Growing'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE)
    location_name = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    planted_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    slip_url = models.FileField(upload_to='slips/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.tree.name} ({self.status})"

    def save(self, *args, **kwargs):
        # ✅ คำนวณราคาต้นไม้ตามจำนวน
        if self.tree and self.quantity:
            self.total_price = self.tree.price * self.quantity
        else:
            self.total_price = 0
        super().save(*args, **kwargs)


class UserEquipment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'รอตรวจสอบ'),       # ผู้ใช้อัปโหลดสลิปแล้ว
        ('verifying', 'กำลังตรวจสอบ'),   # แอดมินกำลังตรวจสลิป
        ('confirmed', 'ยืนยันแล้ว'),     # แอดมินอนุมัติสลิป
        ('shipping', 'กำลังจัดส่ง'),     # แพ็คของ/ส่ง
        ('delivered', 'จัดส่งสำเร็จ'),   # ถึงมือแล้ว
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255, blank=True)
    image_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='equipment/', blank=True, null=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    address = models.CharField(max_length=255, blank=True)
    tel = models.CharField(max_length=20, blank=True)
    payment_slip = models.ImageField(upload_to='slips/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.equipment and self.quantity:
            self.total_price = self.equipment.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.equipment.name} x{self.quantity}"

    @property
    def image_preview(self):
        return self.equipment.image.url if self.equipment and self.equipment.image else ""


    




