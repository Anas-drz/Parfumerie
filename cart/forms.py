from django import forms


PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES,
        coerce=int,
        initial=1,
        label="Quantité",
        widget=forms.Select(attrs={
            'class': 'form-control quantity-select',
            'onchange': 'updateQuantity(this)'
        })
    )
    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 1 or quantity > 20:
            raise forms.ValidationError("La quantité doit être comprise entre 1 et 20.")
        return quantity


class CartUpdateForm(forms.Form):
    """
    Formulaire spécialement conçu pour la mise à jour des quantités
    """
    quantity = forms.IntegerField(
        min_value=0,
        max_value=20,
        initial=1,
        label="Quantité",
        widget=forms.NumberInput(attrs={
            'class': 'form-control quantity-input',
            'min': '0',
            'max': '20',
            'step': '1'
        })
    )

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 0 or quantity > 20:
            raise forms.ValidationError("La quantité doit être comprise entre 0 et 20.")
        return quantity

