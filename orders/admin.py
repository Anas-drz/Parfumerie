from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'payment_method', 'paid', 'payment_status', 'get_total_cost', 'created']
    list_filter = ['paid', 'payment_method', 'payment_status', 'created', 'updated']
    search_fields = ['first_name', 'last_name', 'email', 'id']
    inlines = [OrderItemInline]
    readonly_fields = ['paypal_payment_id', 'paypal_payer_id', 'created', 'updated']
    
    fieldsets = (
        ('Informations client', {
            'fields': ('customer', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Adresse de livraison', {
            'fields': ('address', 'postal_code', 'city')
        }),
        ('Paiement', {
            'fields': ('payment_method', 'paid', 'payment_status', 'paypal_payment_id', 'paypal_payer_id')
        }),
        ('Dates', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )
    
    def get_total_cost(self, obj):
        return f"{obj.get_total_cost()} DH"
    get_total_cost.short_description = 'Total'
    get_total_cost.admin_order_field = 'id'

