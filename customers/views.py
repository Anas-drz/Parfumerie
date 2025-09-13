from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Customer
from .forms import (
    CustomUserCreationForm, 
    CustomAuthenticationForm, 
    UserProfileForm, 
    CustomerProfileForm,
    PasswordChangeForm
)


def register_view(request):
    """
    Vue d'inscription des utilisateurs
    """
    if request.user.is_authenticated:
        return redirect('products:product_list')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Compte créé avec succès pour {username}! Vous pouvez maintenant vous connecter.')
            
            # Connecter automatiquement l'utilisateur après l'inscription
            user = authenticate(username=user.username, password=form.cleaned_data.get('password1'))
            if user:
                login(request, user)
                messages.success(request, f'Bienvenue {user.first_name}!')
                return redirect('products:product_list')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'title': 'Créer un compte'
    }
    return render(request, 'customers/register.html', context)


def login_view(request):
    """
    Vue de connexion des utilisateurs
    """
    if request.user.is_authenticated:
        return redirect('products:product_list')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue {user.first_name}!')
                
                # Rediriger vers la page demandée ou la page d'accueil
                next_page = request.GET.get('next', 'products:product_list')
                return redirect(next_page)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = CustomAuthenticationForm()
    
    context = {
        'form': form,
        'title': 'Se connecter'
    }
    return render(request, 'customers/login.html', context)


def logout_view(request):
    """
    Vue de déconnexion des utilisateurs
    """
    if request.user.is_authenticated:
        username = request.user.first_name or request.user.username
        logout(request)
        messages.success(request, f'Au revoir {username}! Vous avez été déconnecté.')
    return redirect('products:product_list')


@login_required
def profile_view(request):
    """
    Vue du profil utilisateur
    """
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        # Créer un profil client si il n'existe pas
        customer = Customer.objects.create(user=request.user)
    
    context = {
        'customer': customer,
        'title': 'Mon Profil'
    }
    return render(request, 'customers/profile.html', context)


@login_required
def profile_edit_view(request):
    """
    Vue de modification du profil utilisateur
    """
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        customer = Customer.objects.create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        customer_form = CustomerProfileForm(request.POST, instance=customer)
        
        if user_form.is_valid() and customer_form.is_valid():
            user_form.save()
            customer_form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('customers:profile')
    else:
        user_form = UserProfileForm(instance=request.user)
        customer_form = CustomerProfileForm(instance=customer)
    
    context = {
        'user_form': user_form,
        'customer_form': customer_form,
        'title': 'Modifier mon profil'
    }
    return render(request, 'customers/profile_edit.html', context)


@login_required
def password_change_view(request):
    """
    Vue de changement de mot de passe
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre mot de passe a été modifié avec succès.')
            return redirect('customers:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'title': 'Changer mon mot de passe'
    }
    return render(request, 'customers/password_change.html', context)


@login_required
def account_delete_view(request):
    """
    Vue de suppression du compte utilisateur
    """
    if request.method == 'POST':
        user = request.user
        username = user.first_name or user.username
        user.delete()
        messages.success(request, f'Votre compte a été supprimé avec succès. Au revoir {username}!')
        return redirect('products:product_list')
    
    context = {
        'title': 'Supprimer mon compte'
    }
    return render(request, 'customers/account_delete.html', context)


def check_username_availability(request):
    """
    API pour vérifier la disponibilité d'un nom d'utilisateur
    """
    if request.method == 'GET':
        username = request.GET.get('username', '')
        if username:
            is_available = not User.objects.filter(username=username).exists()
            return JsonResponse({'available': is_available})
    return JsonResponse({'available': False})


def check_email_availability(request):
    """
    API pour vérifier la disponibilité d'une adresse email
    """
    if request.method == 'GET':
        email = request.GET.get('email', '')
        user_id = request.GET.get('user_id', None)
        
        if email:
            query = User.objects.filter(email=email)
            if user_id:
                query = query.exclude(id=user_id)
            is_available = not query.exists()
            return JsonResponse({'available': is_available})
    return JsonResponse({'available': False})

