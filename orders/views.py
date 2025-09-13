from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from paypal.standard.forms import PayPalPaymentsForm
from cart.cart import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm
import uuid


@login_required
def order_create(request):
    cart = Cart(request)
    
    # Créer un profil Customer si il n'existe pas
    from customers.models import Customer
    customer, created = Customer.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = customer
            order.save()
            
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            # Vider le panier
            cart.clear()
            
            # Rediriger selon le mode de paiement choisi
            if order.payment_method == 'online':
                return redirect('orders:payment', order_id=order.id)
            else:  # cash_on_delivery
                return redirect('orders:payment_cash_on_delivery', order_id=order.id)
    else:
        form = OrderCreateForm()
    
    return render(request, 'orders/order/create.html', {
        'cart': cart,
        'form': form
    })


@login_required
def payment(request, order_id):
    # Créer un profil Customer si il n'existe pas
    from customers.models import Customer
    customer, created = Customer.objects.get_or_create(user=request.user)
    
    order = get_object_or_404(Order, id=order_id, customer=customer)
    
    # Vérifier que la commande n'est pas déjà payée
    if order.paid:
        return redirect('orders:payment_done')
    
    host = request.get_host()
    
    # Configuration PayPal plus robuste
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': '%.2f' % order.get_total_cost(),
        'item_name': f'Parfumerie Anas - Commande #{order.id}',
        'invoice': str(order.id),
        'currency_code': 'USD',  # Changer en USD pour plus de compatibilité
        'notify_url': request.build_absolute_uri(reverse('paypal-ipn')),
        'return_url': request.build_absolute_uri(reverse('orders:payment_done')),
        'cancel_return': request.build_absolute_uri(reverse('orders:payment_cancelled')),
        'custom': str(order.id),
        # Paramètres additionnels pour améliorer la compatibilité
        'cmd': '_xclick',
        'no_note': '1',
        'no_shipping': '1',
        'rm': '2',  # Return method POST
        'charset': 'utf-8',
    }
    
    try:
        form = PayPalPaymentsForm(initial=paypal_dict)
    except Exception as e:
        # En cas d'erreur avec PayPal, rediriger vers une page d'erreur
        return render(request, 'orders/payment/error.html', {
            'order': order,
            'error': str(e)
        })
    
    return render(request, 'orders/payment/payment.html', {
        'order': order,
        'form': form,
        'paypal_test': settings.PAYPAL_TEST
    })


@csrf_exempt
def payment_done(request):
    return render(request, 'orders/payment/done.html')


@csrf_exempt
def payment_cancelled(request):
    return render(request, 'orders/payment/cancelled.html')



@login_required
def payment_cash_on_delivery(request, order_id):
    """Vue pour confirmer une commande avec paiement à la livraison"""
    from customers.models import Customer
    customer, created = Customer.objects.get_or_create(user=request.user)
    
    order = get_object_or_404(Order, id=order_id, customer=customer)
    
    # Marquer la commande comme confirmée (mais pas encore payée)
    order.payment_status = 'pending'
    order.save()
    
    return render(request, 'orders/payment/cash_on_delivery.html', {
        'order': order
    })

