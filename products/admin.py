from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'display_price', 'discount_info', 'price', 'original_price', 'stock_quantity', 'stock_status', 'available', 'created']
    list_filter = ['available', 'created', 'updated', 'category']
    list_editable = ['price', 'original_price', 'available', 'stock_quantity']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    
    def display_price(self, obj):
        """Affiche le prix avec réduction si applicable"""
        if obj.has_discount:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">{} DH</span><br>'
                '<span style="color: #d4af37; font-weight: bold;">{} DH</span>',
                obj.original_price, obj.price
            )
        else:
            return format_html(
                '<span style="color: #d4af37; font-weight: bold;">{} DH</span>',
                obj.price
            )
    display_price.short_description = 'Prix'
    
    def discount_info(self, obj):
        """Affiche les informations de réduction"""
        if obj.has_discount:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">-{}%</span>',
                obj.discount_percentage
            )
        else:
            return format_html('<span style="color: #999;">Aucune</span>')
    discount_info.short_description = 'Réduction'
    
    def stock_status(self, obj):
        """Affiche le statut du stock avec des couleurs"""
        if obj.stock_quantity == 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">Épuisé</span>'
            )
        elif obj.stock_quantity <= 5:
            return format_html(
                '<span style="color: orange; font-weight: bold;">Stock faible</span>'
            )
        else:
            return format_html(
                '<span style="color: green; font-weight: bold;">En stock</span>'
            )
    
    stock_status.short_description = 'Statut du stock'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Prix et réductions', {
            'fields': ('price', 'original_price', 'stock_quantity', 'available'),
            'description': 'Prix actuel et prix original (avant réduction). Laissez le prix original vide s\'il n\'y a pas de réduction.'
        }),
        ('Image', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
    )

