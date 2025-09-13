from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:product_list_by_category', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Prix original avant réduction")
    available = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(default=0, help_text="Quantité en stock")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['id', 'slug']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:product_detail', args=[self.id, self.slug])
    
    @property
    def is_in_stock(self):
        """Vérifie si le produit est en stock"""
        return self.stock_quantity > 0
    
    @property
    def is_available_for_purchase(self):
        """Vérifie si le produit est disponible à l'achat"""
        return self.available and self.is_in_stock
    
    @property
    def has_discount(self):
        """Vérifie si le produit a une réduction"""
        return self.original_price and self.original_price > self.price
    
    @property
    def discount_percentage(self):
        """Calcule le pourcentage de réduction"""
        if self.has_discount:
            return round(((self.original_price - self.price) / self.original_price) * 100)
        return 0

