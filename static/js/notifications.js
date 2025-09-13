/**
 * Système de notifications modernes pour l'application de parfumerie
 * Remplace les messages Django par des toasts élégants et temporaires
 */

class NotificationSystem {
    constructor() {
        this.container = null;
        this.notifications = new Map();
        this.init();
    }

    init() {
        // Créer le conteneur de notifications
        this.createContainer();
        
        // Intercepter les messages Django existants
        this.interceptDjangoMessages();
        
        // Écouter les événements personnalisés
        this.setupEventListeners();
    }

    createContainer() {
        this.container = document.createElement('div');
        this.container.className = 'notification-container';
        this.container.innerHTML = '';
        document.body.appendChild(this.container);
    }

    interceptDjangoMessages() {
        // Intercepter les messages Django au chargement de la page
        const djangoMessages = document.querySelectorAll('.messages .alert, .alert');
        djangoMessages.forEach(message => {
            const text = message.textContent.trim();
            const type = this.getDjangoMessageType(message);
            if (text) {
                this.show(text, type, 4000);
                message.style.display = 'none';
            }
        });
    }

    getDjangoMessageType(element) {
        if (element.classList.contains('alert-success') || element.classList.contains('success')) {
            return 'success';
        } else if (element.classList.contains('alert-danger') || element.classList.contains('error')) {
            return 'error';
        } else if (element.classList.contains('alert-warning') || element.classList.contains('warning')) {
            return 'warning';
        } else if (element.classList.contains('alert-info') || element.classList.contains('info')) {
            return 'info';
        }
        return 'info';
    }

    setupEventListeners() {
        // Écouter les événements personnalisés
        document.addEventListener('notification:show', (e) => {
            this.show(e.detail.message, e.detail.type, e.detail.duration);
        });

        document.addEventListener('cart:updated', (e) => {
            this.show('Panier mis à jour avec succès', 'success', 3000);
        });

        document.addEventListener('cart:item-added', (e) => {
            this.show(`${e.detail.productName} ajouté au panier`, 'success', 3000);
        });

        document.addEventListener('cart:item-removed', (e) => {
            this.show(`${e.detail.productName} supprimé du panier`, 'info', 3000);
        });

        document.addEventListener('cart:quantity-updated', (e) => {
            this.show(`Quantité mise à jour pour ${e.detail.productName}`, 'success', 2500);
        });
    }

    show(message, type = 'info', duration = 4000) {
        const id = this.generateId();
        const notification = this.createNotification(id, message, type, duration);
        
        this.container.appendChild(notification);
        this.notifications.set(id, notification);

        // Animation d'entrée
        requestAnimationFrame(() => {
            notification.classList.add('show');
        });

        // Auto-suppression
        if (duration > 0) {
            setTimeout(() => {
                this.hide(id);
            }, duration);
        }

        return id;
    }

    createNotification(id, message, type, duration) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.dataset.id = id;

        const icon = this.getIcon(type);
        
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">${icon}</div>
                <div class="notification-message">${message}</div>
                <button class="notification-close" onclick="notificationSystem.hide('${id}')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
            ${duration > 0 ? `<div class="notification-progress" style="animation-duration: ${duration}ms;"></div>` : ''}
        `;

        return notification;
    }

    getIcon(type) {
        const icons = {
            success: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20,6 9,17 4,12"></polyline></svg>',
            error: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>',
            warning: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
            info: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>'
        };
        return icons[type] || icons.info;
    }

    hide(id) {
        const notification = this.notifications.get(id);
        if (notification) {
            notification.classList.add('hide');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
                this.notifications.delete(id);
            }, 300);
        }
    }

    hideAll() {
        this.notifications.forEach((notification, id) => {
            this.hide(id);
        });
    }

    generateId() {
        return 'notification-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    }

    // Méthodes de convenance
    success(message, duration = 3000) {
        return this.show(message, 'success', duration);
    }

    error(message, duration = 5000) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration = 4000) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration = 3000) {
        return this.show(message, 'info', duration);
    }
}

// Initialiser le système de notifications
let notificationSystem;
document.addEventListener('DOMContentLoaded', () => {
    notificationSystem = new NotificationSystem();
    
    // Exposer globalement pour faciliter l'utilisation
    window.notify = notificationSystem;
    window.notificationSystem = notificationSystem;
});

// Intercepter les requêtes AJAX pour afficher les notifications
document.addEventListener('DOMContentLoaded', () => {
    // Intercepter les réponses fetch
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        return originalFetch.apply(this, args).then(response => {
            // Vérifier s'il y a des messages dans les headers ou le body
            if (response.headers.get('X-Notification-Message')) {
                const message = response.headers.get('X-Notification-Message');
                const type = response.headers.get('X-Notification-Type') || 'info';
                notificationSystem.show(message, type);
            }
            return response;
        });
    };

    // Intercepter les soumissions de formulaires
    document.addEventListener('submit', (e) => {
        const form = e.target;
        if (form.method.toLowerCase() === 'post') {
            // Ajouter un indicateur de chargement
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.textContent || submitBtn.value;
                submitBtn.disabled = true;
                submitBtn.textContent = 'Chargement...';
                
                // Restaurer après un délai
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }, 2000);
            }
        }
    });
});

