from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('payment/cash-on-delivery/<int:order_id>/', views.payment_cash_on_delivery, name='payment_cash_on_delivery'),
    path('payment/done/', views.payment_done, name='payment_done'),
    path('payment/cancelled/', views.payment_cancelled, name='payment_cancelled'),
]

