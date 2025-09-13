from django.urls import path
from . import views
from . import search_api

app_name = 'products'

urlpatterns = [
    # URLs publiques
    path('', views.product_list, name='product_list'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # APIs de recherche
    path('api/search/', search_api.search_products_api, name='search_api'),
    path('api/suggestions/', search_api.get_product_suggestions, name='suggestions_api'),
    
    # URLs de gestion des produits (pour le personnel)
    path('manage/', views.product_manage_list, name='product_manage_list'),
    path('manage/create/', views.product_create, name='product_create'),
    path('manage/<int:id>/', views.product_manage_detail, name='product_manage_detail'),
    path('manage/<int:id>/edit/', views.product_update, name='product_update'),
    path('manage/<int:id>/delete/', views.product_delete, name='product_delete'),
    path('manage/<int:id>/toggle-availability/', views.product_toggle_availability, name='product_toggle_availability'),
    
    # URLs de gestion des catégories (pour le personnel)
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:id>/edit/', views.category_update, name='category_update'),
    path('categories/<int:id>/delete/', views.category_delete, name='category_delete'),
]

