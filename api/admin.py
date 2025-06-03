from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MobileUser, DeviceToken, GestureData, Product, Order, ProductReview
from .tasks import generate_product_with_ai

@admin.register(MobileUser)
class MobileUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'is_verified', 'last_login_ip')
    list_filter = ('is_verified', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('-date_joined',)

@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_type', 'is_active', 'last_used')
    list_filter = ('token_type', 'is_active')
    search_fields = ('user__username', 'token')
    ordering = ('-last_used',)

@admin.action(description="Générer un produit IA")
def generate_ai_product(modeladmin, request, queryset):
    generate_product_with_ai.delay()
    modeladmin.message_user(request, "Tâche IA lancée.")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'is_ai_generated', 'created_at')
    list_filter = ('is_ai_generated',)
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    actions = [generate_ai_product]

    def get_queryset(self, request):
        # Add select_related for better performance
        return super().get_queryset(request).select_related()

    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            # Check if product has any orders with PROTECT
            has_orders = obj.orders.filter(status__in=['pending', 'paid', 'shipped']).exists()
            if has_orders:
                return False
        return super().has_delete_permission(request, obj)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'product__name')
    ordering = ('-created_at',)
    readonly_fields = ('total_price', 'created_at', 'updated_at')

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user__username', 'product__name', 'comment')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(GestureData)
class GestureDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'gesture_type', 'confidence_score', 'processed', 'timestamp')
    list_filter = ('gesture_type', 'processed')
    search_fields = ('user__username', 'gesture_type')
    ordering = ('-timestamp',)
