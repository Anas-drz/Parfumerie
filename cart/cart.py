from decimal import Decimal
from django.conf import settings
from products.models import Product


class Cart:
    def __init__(self, request):
        """
        Initialiser le panier.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Sauvegarder un panier vide dans la session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Ajouter un produit au panier ou mettre à jour sa quantité.
        """
        if not isinstance(product, Product):
            raise ValueError("Le produit doit être une instance de Product")
        
        if not product.available:
            raise ValueError(f"Le produit '{product.name}' n'est pas disponible")
        
        if quantity <= 0:
            raise ValueError("La quantité doit être supérieure à 0")
        
        if quantity > 20:
            raise ValueError("La quantité ne peut pas dépasser 20")
        
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price),
                'name': product.name,  # Stocker le nom pour référence rapide
                'available': product.available
            }
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            new_quantity = self.cart[product_id]['quantity'] + quantity
            if new_quantity > 20:
                raise ValueError("La quantité totale ne peut pas dépasser 20")
            self.cart[product_id]['quantity'] = new_quantity
        
        # Mettre à jour les informations du produit au cas où elles auraient changé
        self.cart[product_id]['price'] = str(product.price)
        self.cart[product_id]['name'] = product.name
        self.cart[product_id]['available'] = product.available
        
        self.save()

    def save(self):
        """
        Marquer la session comme "modifiée" pour s'assurer qu'elle soit sauvegardée
        """
        self.session.modified = True

    def remove(self, product):
        """
        Supprimer un produit du panier.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
            return True
        return False

    def update_quantity(self, product, quantity):
        """
        Mettre à jour la quantité d'un produit spécifique
        """
        if quantity <= 0:
            return self.remove(product)
        else:
            self.add(product, quantity, override_quantity=True)
            return True

    def get_item(self, product_id):
        """
        Récupérer un élément spécifique du panier
        """
        return self.cart.get(str(product_id))

    def has_product(self, product):
        """
        Vérifier si un produit est dans le panier
        """
        return str(product.id) in self.cart

    def get_product_quantity(self, product):
        """
        Récupérer la quantité d'un produit spécifique
        """
        product_id = str(product.id)
        if product_id in self.cart:
            return self.cart[product_id]['quantity']
        return 0

    def __iter__(self):
        """
        Itérer sur les éléments du panier et récupérer les produits depuis la base de données.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        for product in products:
            item = self.cart[str(product.id)]
            price = Decimal(item['price'])   # نحولها من str إلى Decimal مؤقتاً
            total_price = price * item['quantity']

            yield {
                'product': product,
                'price': price,
                'quantity': item['quantity'],
                'total_price': total_price,
                'name': item['name'],
                'available': item['available'],
            }

    def __len__(self):
        """
        Compter tous les éléments dans le panier.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Calculer le coût total des éléments dans le panier.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def get_total_items(self):
        """
        Obtenir le nombre total d'articles (différent de la quantité totale)
        """
        return len(self.cart)

    def is_empty(self):
        """
        Vérifier si le panier est vide
        """
        return len(self.cart) == 0

    def clear(self):
        """
        Supprimer le panier de la session.
        """
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.save()

    def clean_unavailable_products(self):
        """
        Supprimer les produits non disponibles du panier
        """
        product_ids = list(self.cart.keys())
        available_products = Product.objects.filter(
            id__in=product_ids, 
            available=True
        ).values_list('id', flat=True)
        
        available_ids = [str(pid) for pid in available_products]
        removed_products = []
        
        for product_id in product_ids:
            if product_id not in available_ids:
                product_name = self.cart[product_id].get('name', 'Produit inconnu')
                removed_products.append(product_name)
                del self.cart[product_id]
        
        if removed_products:
            self.save()
        
        return removed_products

    def get_cart_data(self):
        """
        Retourner les données du panier sous forme de dictionnaire pour l'API
        """
        return {
            'items': [
                {
                    'product_id': item['product'].id,
                    'name': item['name'],
                    'quantity': item['quantity'],
                    'price': str(item['price']),
                    'total_price': str(item['total_price']),
                    'available': item['available'],
                }
                for item in self
            ],
            'total_price': str(self.get_total_price()),
            'total_quantity': len(self),
            'total_items': self.get_total_items(),
            'is_empty': self.is_empty()
        }

