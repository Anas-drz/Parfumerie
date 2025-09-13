from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import Category, Product
from .forms import ProductForm, CategoryForm, ProductSearchForm
from cart.forms import CartAddProductForm


def product_list(request, category_slug=None):
    """
    Afficher la liste des produits avec filtrage et recherche
    """
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    # Filtrer par catégorie si spécifiée
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Formulaire de recherche
    search_form = ProductSearchForm(request.GET)
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        search_category = search_form.cleaned_data.get('category')
        available_only = search_form.cleaned_data.get('available_only')
        sort_by = search_form.cleaned_data.get('sort_by')
        
        # Appliquer les filtres de recherche
        if query:
            products = products.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )
        
        if search_category:
            products = products.filter(category=search_category)
            category = search_category
        
        if not available_only:
            products = Product.objects.all()
            if category_slug or search_category:
                products = products.filter(category=category)
        
        if sort_by:
            products = products.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 produits par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'categories': categories,
        'products': page_obj,
        'search_form': search_form,
        'page_obj': page_obj,
    }
    
    return render(request, 'products/product/list.html', context)


def product_detail(request, id, slug):
    """
    Afficher les détails d'un produit
    """
    product = get_object_or_404(Product, id=id, slug=slug)
    cart_product_form = CartAddProductForm()
    
    # Produits similaires (même catégorie)
    similar_products = Product.objects.filter(
        category=product.category,
        available=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'cart_product_form': cart_product_form,
        'similar_products': similar_products,
    }
    
    return render(request, 'products/product/detail.html', context)


# Vues CRUD pour l'administration des produits (nécessitent une authentification)

def is_staff_user(user):
    """
    Vérifier si l'utilisateur est un membre du personnel
    """
    return user.is_authenticated and user.is_staff


@user_passes_test(is_staff_user)
def product_manage_list(request):
    """
    Liste de gestion des produits pour les administrateurs
    """
    products = Product.objects.all().select_related('category')
    
    # Recherche et filtrage
    search_form = ProductSearchForm(request.GET)
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        category = search_form.cleaned_data.get('category')
        available_only = search_form.cleaned_data.get('available_only')
        sort_by = search_form.cleaned_data.get('sort_by')
        
        if query:
            products = products.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )
        
        if category:
            products = products.filter(category=category)
        
        if available_only:
            products = products.filter(available=True)
        
        if sort_by:
            products = products.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'search_form': search_form,
        'page_obj': page_obj,
    }
    
    return render(request, 'products/manage/product_list.html', context)


@user_passes_test(is_staff_user)
def product_create(request):
    """
    Créer un nouveau produit
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Le produit '{product.name}' a été créé avec succès.")
            return redirect('products:product_manage_detail', product.id)
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Créer un nouveau produit',
        'action': 'create'
    }
    
    return render(request, 'products/manage/product_form.html', context)


@user_passes_test(is_staff_user)
def product_update(request, id):
    """
    Modifier un produit existant
    """
    product = get_object_or_404(Product, id=id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Le produit '{product.name}' a été modifié avec succès.")
            return redirect('products:product_manage_detail', product.id)
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'title': f'Modifier {product.name}',
        'action': 'update'
    }
    
    return render(request, 'products/manage/product_form.html', context)


@user_passes_test(is_staff_user)
def product_delete(request, id):
    """
    Supprimer un produit
    """
    product = get_object_or_404(Product, id=id)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f"Le produit '{product_name}' a été supprimé avec succès.")
        return redirect('products:product_manage_list')
    
    context = {
        'product': product,
        'title': f'Supprimer {product.name}'
    }
    
    return render(request, 'products/manage/product_confirm_delete.html', context)


@user_passes_test(is_staff_user)
def product_manage_detail(request, id):
    """
    Détails d'un produit pour la gestion
    """
    product = get_object_or_404(Product, id=id)
    
    context = {
        'product': product,
    }
    
    return render(request, 'products/manage/product_detail.html', context)


# Vues CRUD pour les catégories

@user_passes_test(is_staff_user)
def category_list(request):
    """
    Liste des catégories pour la gestion
    """
    categories = Category.objects.all().order_by('name')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'products/manage/category_list.html', context)


@user_passes_test(is_staff_user)
def category_create(request):
    """
    Créer une nouvelle catégorie
    """
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"La catégorie '{category.name}' a été créée avec succès.")
            return redirect('products:category_list')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'title': 'Créer une nouvelle catégorie',
        'action': 'create'
    }
    
    return render(request, 'products/manage/category_form.html', context)


@user_passes_test(is_staff_user)
def category_update(request, id):
    """
    Modifier une catégorie existante
    """
    category = get_object_or_404(Category, id=id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"La catégorie '{category.name}' a été modifiée avec succès.")
            return redirect('products:category_list')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'title': f'Modifier {category.name}',
        'action': 'update'
    }
    
    return render(request, 'products/manage/category_form.html', context)


@user_passes_test(is_staff_user)
def category_delete(request, id):
    """
    Supprimer une catégorie
    """
    category = get_object_or_404(Category, id=id)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f"La catégorie '{category_name}' a été supprimée avec succès.")
        return redirect('products:category_list')
    
    # Vérifier s'il y a des produits dans cette catégorie
    products_count = category.products.count()
    
    context = {
        'category': category,
        'products_count': products_count,
        'title': f'Supprimer {category.name}'
    }
    
    return render(request, 'products/manage/category_confirm_delete.html', context)


# API pour les requêtes AJAX

@user_passes_test(is_staff_user)
def product_toggle_availability(request, id):
    """
    Basculer la disponibilité d'un produit via AJAX
    """
    if request.method == 'POST':
        product = get_object_or_404(Product, id=id)
        product.available = not product.available
        product.save()
        
        return JsonResponse({
            'success': True,
            'available': product.available,
            'message': f"Produit {'activé' if product.available else 'désactivé'}"
        })
    
    return JsonResponse({'success': False})

