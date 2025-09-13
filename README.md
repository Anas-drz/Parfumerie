# Projet Parfumerie

Ce projet est une application web de commerce électronique développée avec Django, conçue pour la vente de produits de parfumerie. Il intègre des fonctionnalités de gestion de produits, de panier d'achat, de commandes, de gestion des utilisateurs et un système de paiement via PayPal.

## Fonctionnalités

- **Gestion des produits** : Ajout, modification et suppression de produits de parfumerie avec détails (nom, description, prix, images).
- **Panier d'achat** : Les utilisateurs peuvent ajouter des produits à leur panier, ajuster les quantités et supprimer des articles.
- **Gestion des commandes** : Suivi des commandes, historique des achats pour les utilisateurs enregistrés.
- **Authentification et Autorisation** : Système de connexion/déconnexion, enregistrement des utilisateurs, gestion des sessions.
- **Intégration PayPal** : Traitement sécurisé des paiements via PayPal.
- **Sécurité** : Utilisation de Django Axes pour la protection contre les attaques par force brute.

## Technologies Utilisées

- **Backend** : Python, Django
- **Base de données** : SQLite3 (pour le développement, peut être configuré pour PostgreSQL/MySQL en production)
- **Paiement** : PayPal IPN (Instant Payment Notification)
- **Sécurité** : Django Axes
- **Dépendances Python** : django-paypal, django-axes, python-dotenv

## Installation

Suivez ces étapes pour configurer et exécuter le projet localement :

1. Cloner le dépôt 

2. Créer et activer un environnement virtuel 

3. Installer les dépendances 

4. Configuration des variables d'environnement 

5. Appliquer les migrations de la base de données 

6. Créer un superutilisateur (pour accéder à l'interface d'administration) 

7. Lancer le serveur de développement

## Structure du Projet
```shell
parfumerie/
├── manage.py
├── parfumerie/             # Dossier principal du projet Django
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py         # Configuration du projet
│   ├── urls.py             # URL principales du projet
│   └── wsgi.py
├── cart/                   # Application de gestion du panier
├── customers/              # Application de gestion des clients/utilisateurs
├── orders/                 # Application de gestion des commandes
├── products/               # Application de gestion des produits
├── static/                 # Fichiers statiques personnalisés
├── staticfiles/            # Fichiers statiques collectés (pour la production)
├── media/                  # Fichiers médias (images de produits, etc.)
└── db.sqlite3              # Base de données SQLite (en développement)

