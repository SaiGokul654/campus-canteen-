from django.contrib import admin
from .models import Category, Dish, Review, PreOrder, PickupSlot

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'dish_type', 'price', 'is_available', 'is_featured']
    list_filter = ['category', 'dish_type', 'is_available', 'is_featured']
    search_fields = ['name', 'description']
    list_editable = ['is_available', 'is_featured', 'price']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'dish', 'rating', 'created_at']
    list_filter = ['rating', 'created_at', 'dish__category']
    search_fields = ['user__username', 'dish__name', 'comment']
    readonly_fields = ['created_at']

@admin.register(PreOrder)
class PreOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'dish', 'quantity', 'pickup_slot', 'date', 'status', 'total_amount']
    list_filter = ['status', 'date', 'pickup_slot', 'dish__category']
    search_fields = ['order_number', 'user__username', 'dish__name']
    list_editable = ['status']
    readonly_fields = ['order_number', 'total_amount', 'created_at', 'updated_at']
    date_hierarchy = 'date'

@admin.register(PickupSlot)
class PickupSlotAdmin(admin.ModelAdmin):
    list_display = ['start_time', 'end_time', 'max_orders', 'is_active']
    list_filter = ['is_active']
    list_editable = ['max_orders', 'is_active']