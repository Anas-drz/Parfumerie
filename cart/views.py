from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from products.models import Product
from .cart import Cart
from .forms import CartAddProductForm
import json
from django.http import HttpResponse


@require_POST
def cart_add(request, product_id):
    """
    Ajouter un produit au panier
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    # Vérifier la disponibilité et le stock
    if not product.is_available_for_purchase:
        if not product.available:
            response = redirect('products:product_detail', product.id, product.slug)
            response['X-Notification-Message'] = f"Le produit '{product.name}' n'est pas disponible."
            response['X-Notification-Type'] = 'error'
            return response
        elif not product.is_in_stock:
            response = redirect('products:product_detail', product.id, product.slug)
            response['X-Notification-Message'] = f"Le produit '{product.name}' est épuisé."
            response['X-Notification-Type'] = 'error'
            return response
    
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        requested_quantity = cd['quantity']
        
        # Vérifier si la quantité demandée est disponible
        current_cart_quantity = cart.cart.get(str(product_id), {}).get('quantity', 0)
        total_requested = current_cart_quantity + requested_quantity if not cd['override'] else requested_quantity
        
        if total_requested > product.stock_quantity:
            available_quantity = product.stock_quantity - (current_cart_quantity if not cd['override'] else 0)
            response = redirect('products:product_detail', product.id, product.slug)
            response['X-Notification-Message'] = f"Quantité insuffisante en stock. Disponible: {available_quantity}"
            response['X-Notification-Type'] = 'error'
            return response
        
        cart.add(product=product,
                 quantity=requested_quantity,
                 override_quantity=cd['override'])
        
        response = redirect('cart:cart_detail')
        if cd['override']:
            response['X-Notification-Message'] = f"Quantité mise à jour pour '{product.name}'"
            response['X-Notification-Type'] = 'success'
        else:
            response['X-Notification-Message'] = f"'{product.name}' ajouté au panier"
            response['X-Notification-Type'] = 'success'
        return response
    else:
        response = redirect('cart:cart_detail')
        response['X-Notification-Message'] = "Erreur lors de l'ajout du produit au panier"
        response['X-Notification-Type'] = 'error'
        return response


@require_POST
def cart_remove(request, product_id):
    """
    Supprimer un produit du panier
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    
    response = redirect('cart:cart_detail')
    response['X-Notification-Message'] = f"'{product.name}' supprimé du panier"
    response['X-Notification-Type'] = 'info'
    return response


@require_POST
def cart_update(request, product_id):
    """
    Mettre à jour la quantité d'un produit dans le panier
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1
    
    if quantity > 0:
        # Vérifier le stock disponible
        if quantity > product.stock_quantity:
            message = f"Quantité insuffisante en stock pour '{product.name}'. Disponible: {product.stock_quantity}"
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': message,
                    'available_stock': product.stock_quantity,
                    'notification_type': 'error'
                })
            response = redirect('cart:cart_detail')
            response['X-Notification-Message'] = message
            response['X-Notification-Type'] = 'error'
            return response
        
        cart.add(product=product, quantity=quantity, override_quantity=True)
        message = f"Quantité mise à jour pour '{product.name}'"
        notification_type = 'success'
    else:
        cart.remove(product)
        message = f"'{product.name}' supprimé du panier"
        notification_type = 'info'
    
    # Réponse AJAX pour les mises à jour dynamiques
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': message,
            'notification_type': notification_type,
            'cart_total': str(cart.get_total_price()),
            'cart_count': len(cart),
            'item_total': str(cart.cart.get(str(product_id), {}).get('price', 0)) if quantity > 0 else '0'
        })
    
    response = redirect('cart:cart_detail')
    response['X-Notification-Message'] = message
    response['X-Notification-Type'] = notification_type
    return response


def cart_clear(request):
    """
    Vider complètement le panier
    """
    cart = Cart(request)
    cart.clear()
    
    response = redirect('cart:cart_detail')
    response['X-Notification-Message'] = "Panier vidé avec succès"
    response['X-Notification-Type'] = 'success'
    return response


def cart_detail(request):
    """
    Afficher les détails du panier
    """
    cart = Cart(request)
    
    # Vérifier la disponibilité des produits dans le panier
    unavailable_items = []
    for item in cart:
        product = item['product']
        if not product.is_available_for_purchase:
            unavailable_items.append(item)
        elif item['quantity'] > product.stock_quantity:
            # Ajuster automatiquement la quantité si elle dépasse le stock
            cart.add(product=product, quantity=product.stock_quantity, override_quantity=True)
            messages.warning(request, f"Quantité ajustée pour '{product.name}' (stock disponible: {product.stock_quantity})")
    
    # Supprimer les articles non disponibles
    for item in unavailable_items:
        cart.remove(item['product'])
        messages.warning(request, f"'{item['product'].name}' a été retiré du panier car il n'est plus disponible.")
    
    # Ajouter les formulaires de mise à jour pour chaque élément
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True
        })
        # Ajouter l'information sur le stock disponible
        item['available_stock'] = item['product'].stock_quantity
    
    context = {
        'cart': cart,
        'cart_total': cart.get_total_price(),
        'cart_count': len(cart)
    }
    
    return render(request, 'cart/detail.html', context)


def cart_summary(request):
    """
    Résumé du panier pour la navigation
    """
    cart = Cart(request)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'cart_count': len(cart),
            'cart_total': str(cart.get_total_price())
        })
    
    return redirect('cart:cart_detail')

