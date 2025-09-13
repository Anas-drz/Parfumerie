#!/usr/bin/env python3
"""
Script de test des fonctionnalités principales de la plateforme e-commerce
"""

import os
import sys

# Configuration Django AVANT les imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parfumerie.settings')

import django
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from products.models import Category, Product
from customers.models import Customer
from cart.cart import Cart


def test_models():
    """Test des modèles"""
    print("🧪 Test des modèles...")
    
    # Test Category
    try:
        category = Category.objects.create(name="Test Parfums", slug="test-parfums")
        print("✅ Modèle Category : OK")
    except Exception as e:
        print(f"❌ Modèle Category : {e}")
        return False
    
    # Test Product
    try:
        product = Product.objects.create(
            category=category,
            name="Test Parfum",
            slug="test-parfum",
            price=50.00,
            description="Un parfum de test",
            available=True
        )
        print("✅ Modèle Product : OK")
    except Exception as e:
        print(f"❌ Modèle Product : {e}")
        return False
    
    # Test User et Customer
    try:
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )
        customer = Customer.objects.create(
            user=user,
            phone_number="0123456789",
            address="123 Test Street"
        )
        print("✅ Modèles User et Customer : OK")
    except Exception as e:
        print(f"❌ Modèles User et Customer : {e}")
        return False
    
    return True


def test_urls():
    """Test des URLs principales"""
    print("\n🌐 Test des URLs...")
    
    client = Client()
    
    # URLs à tester
    urls_to_test = [
        ('products:product_list', 200),
        ('customers:login', 200),
        ('customers:register', 200),
        ('cart:cart_detail', 200),
    ]
    
    for url_name, expected_status in urls_to_test:
        try:
            url = reverse(url_name)
            response = client.get(url)
            if response.status_code == expected_status:
                print(f"✅ URL {url_name} : OK (Status: {response.status_code})")
            else:
                print(f"❌ URL {url_name} : Status {response.status_code} (attendu: {expected_status})")
                return False
        except Exception as e:
            print(f"❌ URL {url_name} : {e}")
            return False
    
    return True


def test_cart_functionality():
    """Test des fonctionnalités du panier"""
    print("\n🛒 Test des fonctionnalités du panier...")
    
    try:
        # Créer une session de test
        from django.contrib.sessions.backends.db import SessionStore
        session = SessionStore()
        session.create()
        
        # Simuler une requête avec session
        class MockRequest:
            def __init__(self, session):
                self.session = session
        
        request = MockRequest(session)
        cart = Cart(request)
        
        # Créer un produit de test
        category = Category.objects.get_or_create(name="Test", slug="test")[0]
        product = Product.objects.get_or_create(
            name="Test Product",
            slug="test-product",
            category=category,
            price=25.00,
            defaults={'available': True}
        )[0]
        
        # Test ajout au panier
        cart.add(product, quantity=2)
        if len(cart) == 2:
            print("✅ Ajout au panier : OK")
        else:
            print(f"❌ Ajout au panier : Quantité incorrecte ({len(cart)})")
            return False
        
        # Test prix total
        total = cart.get_total_price()
        if total == 50.00:
            print("✅ Calcul du prix total : OK")
        else:
            print(f"❌ Calcul du prix total : {total} (attendu: 50.00)")
            return False
        
        # Test suppression du panier
        cart.remove(product)
        if len(cart) == 0:
            print("✅ Suppression du panier : OK")
        else:
            print(f"❌ Suppression du panier : Quantité incorrecte ({len(cart)})")
            return False
        
    except Exception as e:
        print(f"❌ Test du panier : {e}")
        return False
    
    return True


def test_authentication():
    """Test des fonctionnalités d'authentification"""
    print("\n🔐 Test des fonctionnalités d'authentification...")
    
    client = Client()
    
    try:
        # Test inscription
        response = client.post(reverse('customers:register'), {
            'username': 'newtestuser',
            'email': 'newtest@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'first_name': 'New',
            'last_name': 'User',
            'phone_number': '0987654321',
            'address': '456 New Street'
        })
        
        if response.status_code in [200, 302]:  # 302 = redirection après succès
            print("✅ Inscription : OK")
        else:
            print(f"❌ Inscription : Status {response.status_code}")
            return False
        
        # Test connexion
        response = client.post(reverse('customers:login'), {
            'username': 'newtestuser',
            'password': 'complexpassword123'
        })
        
        if response.status_code in [200, 302]:
            print("✅ Connexion : OK")
        else:
            print(f"❌ Connexion : Status {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Test d'authentification : {e}")
        return False
    
    return True


def test_admin_functionality():
    """Test des fonctionnalités d'administration"""
    print("\n⚙️ Test des fonctionnalités d'administration...")
    
    try:
        # Créer un superutilisateur
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        client = Client()
        client.login(username='admin', password='adminpass123')
        
        # Test accès aux pages d'administration
        admin_urls = [
            'products:product_manage_list',
            'products:category_list',
            'products:product_create',
            'products:category_create',
        ]
        
        for url_name in admin_urls:
            response = client.get(reverse(url_name))
            if response.status_code == 200:
                print(f"✅ Page admin {url_name} : OK")
            else:
                print(f"❌ Page admin {url_name} : Status {response.status_code}")
                return False
        
    except Exception as e:
        print(f"❌ Test d'administration : {e}")
        return False
    
    return True


def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests de la plateforme e-commerce\n")
    
    tests = [
        test_models,
        test_urls,
        test_cart_functionality,
        test_authentication,
        test_admin_functionality,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Erreur lors du test : {e}")
            failed += 1
    
    print(f"\n📊 Résultats des tests:")
    print(f"✅ Tests réussis : {passed}")
    print(f"❌ Tests échoués : {failed}")
    print(f"📈 Taux de réussite : {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 Tous les tests sont passés avec succès!")
        return True
    else:
        print(f"\n⚠️ {failed} test(s) ont échoué. Veuillez vérifier les erreurs ci-dessus.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

