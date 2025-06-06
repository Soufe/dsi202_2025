from django.contrib import admin
from .models import (
    Tree, PlantingPlan, Equipment, EquipmentOrder,
    UserTree, TreeCare, Notification, UserPlanting, UserEquipment, UserTree
)

@admin.register(Tree)
class TreeAdmin(admin.ModelAdmin):
    list_display = ('name', 'species')
    search_fields = ('name', 'species')

@admin.register(PlantingPlan)
class PlantingPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan_type', 'tree', 'quantity', 'subscribed')
    list_filter = ('plan_type', 'subscribed')
    search_fields = ('user__username', 'tree__name')

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)

@admin.register(EquipmentOrder)
class EquipmentOrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'equipment', 'quantity', 'order_date', 'total_price')
    list_filter = ('order_date',)
    search_fields = ('user__username', 'equipment__name')

@admin.register(UserTree)
class UserTreeAdmin(admin.ModelAdmin):
    list_display = ('user', 'tree', 'location', 'planted_date')
    search_fields = ('user__username', 'tree__name', 'location')

@admin.register(TreeCare)
class TreeCareAdmin(admin.ModelAdmin):
    list_display = ('user_tree', 'care_type', 'care_date')
    list_filter = ('care_type',)
    search_fields = ('user_tree__tree__name',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')
    list_filter = ('is_read',)
    search_fields = ('user__username', 'message')

@admin.register(UserPlanting)
class UserPlantingAdmin(admin.ModelAdmin):
    list_display = ('user', 'tree', 'location_name', 'status', 'planted_date', 'created_at')
    list_filter = ('status', 'planted_date', 'created_at')
    search_fields = ('user__username', 'tree__name', 'location_name')
    ordering = ('-created_at',)

@admin.register(UserEquipment)
class UserEquipmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'equipment', 'quantity', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'equipment__name', 'address', 'tel')
    readonly_fields = ('total_price', 'created_at')

