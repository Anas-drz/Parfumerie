from django.dispatch import receiver
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from .models import Order


@receiver(valid_ipn_received)
def payment_notification(sender, **kwargs):
    """
    Signal handler pour traiter les notifications IPN de PayPal
    """
    ipn_obj = sender
    
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        try:
            order = Order.objects.get(id=ipn_obj.invoice)
            
            # Vérifier que le montant correspond
            if float(ipn_obj.mc_gross) == float(order.get_total_cost()):
                order.paid = True
                order.payment_status = 'completed'
                order.paypal_payment_id = ipn_obj.txn_id
                order.paypal_payer_id = ipn_obj.payer_id
                order.save()
                

                
        except Order.DoesNotExist:
            # Log l'erreur
            pass
    else:
        # Traiter les autres statuts de paiement
        try:
            order = Order.objects.get(id=ipn_obj.invoice)
            if ipn_obj.payment_status in ['Denied', 'Expired', 'Failed']:
                order.payment_status = 'failed'
                order.save()
            elif ipn_obj.payment_status == 'Canceled_Reversal':
                order.payment_status = 'cancelled'
                order.save()
        except Order.DoesNotExist:
            pass

