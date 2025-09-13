from django.http import JsonResponse
from django.db.models import Q
from .models import Product
import json


def search_products_api(request):
    """
    API pour la recherche intelligente de produits
    Retourne les produits qui commencent par la lettre ou le texte saisi
    """
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        
        if not query:
            return JsonResponse({'products': []})
        
        # Rechercher les produits qui commencent par la requête
        products = Product.objects.filter(
            Q(name__istartswith=query) & Q(available=True)
        ).select_related('category')[:10]  # Limiter à 10 résultats
        
        # Formater les résultats
        results = []
        for product in products:
            results.append({
                'id': product.id,
                'name': product.name,
                'slug': product.slug,
                'price': str(product.price),
                'category': product.category.name,
                'image_url': product.image.url if product.image else None,
                'url': product.get_absolute_url()
            })
        
        return JsonResponse({'products': results})
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


def get_product_suggestions(request):
    """
    API pour obtenir des suggestions de produits basées sur les premières lettres
    """
    if request.method == 'GET':
        letter = request.GET.get('letter', '').strip().upper()
        
        if not letter or len(letter) != 1:
            return JsonResponse({'suggestions': []})
        
        # Obtenir tous les produits qui commencent par cette lettre
        products = Product.objects.filter(
            Q(name__istartswith=letter) & Q(available=True)
        ).select_related('category').order_by('name')[:20]
        
        suggestions = []
        for product in products:
            suggestions.append({
                'id': product.id,
                'name': product.name,
                'slug': product.slug,
                'price': str(product.price),
                'category': product.category.name,
                'image_url': product.image.url if product.image else None,
                'url': product.get_absolute_url()
            })
        
        return JsonResponse({'suggestions': suggestions})
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

