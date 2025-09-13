from django import forms
from django.utils.text import slugify
from .models import Product, Category


class CategoryForm(forms.ModelForm):
    """
    Formulaire pour créer et modifier les catégories
    """
    class Meta:
        model = Category
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la catégorie'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL slug (généré automatiquement si vide)'
            })
        }
        labels = {
            'name': 'Nom de la catégorie',
            'slug': 'Slug URL'
        }
        help_texts = {
            'slug': 'Laissez vide pour générer automatiquement à partir du nom'
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        
        # Si le slug est vide, le générer à partir du nom
        if not slug and name:
            slug = slugify(name)
        
        # Vérifier l'unicité du slug
        if slug:
            existing = Category.objects.filter(slug=slug)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError("Ce slug existe déjà. Veuillez en choisir un autre.")
        
        return slug

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance


class ProductForm(forms.ModelForm):
    """
    Formulaire pour créer et modifier les produits
    """
    class Meta:
        model = Product
        fields = ['category', 'name', 'slug', 'image', 'description', 'price', 'available']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du produit'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL slug (généré automatiquement si vide)'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description du produit'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'category': 'Catégorie',
            'name': 'Nom du produit',
            'slug': 'Slug URL',
            'image': 'Image du produit',
            'description': 'Description',
            'price': 'Prix (DH)',
            'available': 'Disponible'
        }
        help_texts = {
            'slug': 'Laissez vide pour générer automatiquement à partir du nom',
            'price': 'Prix en dirhams marocains',
            'available': 'Cochez si le produit est disponible à la vente'
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        
        # Si le slug est vide, le générer à partir du nom
        if not slug and name:
            slug = slugify(name)
        
        # Vérifier l'unicité du slug
        if slug:
            existing = Product.objects.filter(slug=slug)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError("Ce slug existe déjà. Veuillez en choisir un autre.")
        
        return slug

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("Le prix ne peut pas être négatif.")
        return price

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance


class ProductSearchForm(forms.Form):
    """
    Formulaire de recherche de produits
    """
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher un produit...'
        }),
        label='Recherche'
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Toutes les catégories",
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Catégorie'
    )
    available_only = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Produits disponibles uniquement'
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('name', 'Nom (A-Z)'),
            ('-name', 'Nom (Z-A)'),
            ('price', 'Prix (croissant)'),
            ('-price', 'Prix (décroissant)'),
            ('-created', 'Plus récents'),
            ('created', 'Plus anciens'),
        ],
        required=False,
        initial='name',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Trier par'
    )

