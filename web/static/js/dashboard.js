// 🚀 HTTP-MCP Bridge Dashboard - JavaScript principal
// Gestion de l'interface utilisateur, API calls et interactivité

class MCPDashboard {
    constructor() {
        this.baseUrl = window.location.origin;
        this.token = localStorage.getItem('mcp_token');
        this.user = JSON.parse(localStorage.getItem('mcp_user') || '{}');
        this.socket = null;
        this.currentPage = 'dashboard';

        this.init();
    }

    init() {
        console.log('🚀 Initialisation MCP Dashboard');

        // Vérifier l'authentification
        if (!this.token && window.location.pathname !== '/login') {
            this.redirectToLogin();
            return;
        }

        // Initialiser l'interface
        this.setupEventListeners();
        this.setupNavigation();
        this.setupWebSocket();

        // Charger la page actuelle
        this.loadCurrentPage();

        // Actualiser les données toutes les 30 secondes
        setInterval(() => this.refreshData(), 30000);
    }

    setupEventListeners() {
        // Toggle sidebar (mobile)
        const toggleBtn = document.getElementById('sidebar-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleSidebar());
        }

        // Logout
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }

        // Formulaires
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => this.handleNavigation(e));
        });

        // Toggles de permissions
        document.querySelectorAll('.permission-toggle').forEach(toggle => {
            toggle.addEventListener('change', (e) => this.handlePermissionToggle(e));
        });
    }

    setupNavigation() {
        const currentPath = window.location.pathname;
        document.querySelectorAll('.nav-link').forEach(link => {
            const href = link.getAttribute('href');
            if (href === currentPath) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    setupWebSocket() {
        if (!this.token) return;

        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;

            this.socket = new WebSocket(wsUrl);

            this.socket.onopen = () => {
                console.log('✅ WebSocket connecté');
                this.socket.send(JSON.stringify({
                    type: 'auth',
                    token: this.token
                }));
            };

            this.socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };

            this.socket.onclose = () => {
                console.log('❌ WebSocket fermé, reconnexion...');
                setTimeout(() => this.setupWebSocket(), 5000);
            };

            this.socket.onerror = (error) => {
                console.error('❌ Erreur WebSocket:', error);
            };
        } catch (error) {
            console.error('❌ Impossible de créer WebSocket:', error);
        }
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'status_update':
                this.updateStatus(data.payload);
                break;
            case 'new_log':
                this.addLogEntry(data.payload);
                break;
            case 'metrics_update':
                this.updateMetrics(data.payload);
                break;
            case 'permission_change':
                this.refreshPermissions();
                break;
            default:
                console.log('📨 Message WebSocket:', data);
        }
    }

    async apiCall(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (!response.ok) {
                if (response.status === 401) {
                    this.redirectToLogin();
                    return null;
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`❌ Erreur API ${endpoint}:`, error);
            this.showNotification('Erreur de connexion', 'error');
            return null;
        }
    }

    async handleLogin(event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);
        const credentials = {
            username: formData.get('username'),
            password: formData.get('password')
        };

        this.showLoading(true);

        try {
            const response = await this.apiCall('/auth/login', {
                method: 'POST',
                body: JSON.stringify(credentials)
            });

            if (response && response.access_token) {
                this.token = response.access_token;
                this.user = response.user;

                localStorage.setItem('mcp_token', this.token);
                localStorage.setItem('mcp_user', JSON.stringify(this.user));

                this.showNotification('Connexion réussie', 'success');
                window.location.href = '/dashboard';
            } else {
                this.showNotification('Identifiants invalides', 'error');
            }
        } catch (error) {
            this.showNotification('Erreur de connexion', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async logout() {
        try {
            await this.apiCall('/auth/logout', { method: 'POST' });
        } catch (error) {
            console.error('Erreur logout:', error);
        }

        this.token = null;
        this.user = {};
        localStorage.removeItem('mcp_token');
        localStorage.removeItem('mcp_user');

        if (this.socket) {
            this.socket.close();
        }

        this.redirectToLogin();
    }

    redirectToLogin() {
        window.location.href = '/login';
    }

    toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.classList.toggle('collapsed');
        }
    }

    handleNavigation(event) {
        event.preventDefault();
        const href = event.currentTarget.getAttribute('href');

        // Mettre à jour l'état actif
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        event.currentTarget.classList.add('active');

        // Charger la page
        this.loadPage(href);

        // Mettre à jour l'URL
        history.pushState(null, '', href);
    }

    async loadPage(path) {
        const content = document.getElementById('main-content');
        if (!content) return;

        // Mettre à jour le titre de la page
        const pageTitle = this.getPageTitle(path);
        const titleElement = document.getElementById('page-title');
        if (titleElement) {
            titleElement.textContent = pageTitle;
        }

        this.showLoading(true);

        try {
            let templateUrl;
            switch (path) {
                case '/dashboard':
                    templateUrl = '/api/templates/dashboard-overview';
                    break;
                case '/permissions':
                    templateUrl = '/api/templates/permissions';
                    break;
                case '/config':
                    templateUrl = '/api/templates/config';
                    break;
                case '/tools':
                    templateUrl = '/api/templates/tools';
                    break;
                case '/logs':
                    templateUrl = '/api/templates/logs';
                    break;
                case '/admin':
                    templateUrl = '/api/templates/admin';
                    break;
                default:
                    templateUrl = '/api/templates/dashboard-overview';
            }

            const response = await fetch(templateUrl);
            if (!response.ok) {
                throw new Error(`Erreur ${response.status}: ${response.statusText}`);
            }

            const html = await response.text();
            content.innerHTML = html;

            // Exécuter les scripts dans le contenu chargé
            this.executeScripts(content);

            this.currentPage = path.replace('/', '') || 'dashboard';

        } catch (error) {
            console.error('Erreur chargement page:', error);
            content.innerHTML = `
                <div class="text-center py-8">
                    <div class="text-red-500 text-6xl mb-4">⚠️</div>
                    <h3 class="text-xl font-semibold mb-2">Erreur de chargement</h3>
                    <p class="text-secondary">Impossible de charger le contenu de la page: ${error.message}</p>
                    <button class="btn btn-primary mt-4" onclick="dashboard.loadPage('${path}')">
                        Réessayer
                    </button>
                </div>
            `;
        } finally {
            this.showLoading(false);
        }
    }

    getPageTitle(path) {
        const titles = {
            '/dashboard': 'Tableau de bord',
            '/permissions': 'Gestion des permissions',
            '/config': 'Configuration',
            '/tools': 'Outils MCP',
            '/logs': 'Logs système',
            '/admin': 'Administration'
        };
        return titles[path] || 'Dashboard';
    }

    executeScripts(container) {
        const scripts = container.querySelectorAll('script');
        scripts.forEach(script => {
            const newScript = document.createElement('script');
            if (script.src) {
                newScript.src = script.src;
            } else {
                newScript.textContent = script.textContent;
            }
            document.head.appendChild(newScript);
            // Laisser le script s'exécuter, puis le supprimer après un délai
            setTimeout(() => {
                if (newScript.parentNode) {
                    newScript.parentNode.removeChild(newScript);
                }
            }, 100);
        });
    }

    async loadCurrentPage() {
        const path = window.location.pathname;
        await this.loadPage(path);
    }

    async loadDashboard() {
        const content = document.getElementById('main-content');
        if (!content) return;

        // Charger les métriques du dashboard
        const [status, stats, sessions] = await Promise.all([
            this.apiCall('/mcp/status'),
            this.apiCall('/admin/stats'),
            this.apiCall('/auth/sessions')
        ]);

        content.innerHTML = this.renderDashboard(status, stats, sessions);
        this.currentPage = 'dashboard';
    }

    async loadPermissions() {
        const content = document.getElementById('main-content');
        if (!content) return;

        const permissions = await this.apiCall('/permissions/me');
        content.innerHTML = this.renderPermissions(permissions);
        this.currentPage = 'permissions';

        // Réattacher les event listeners pour les toggles
        this.setupPermissionToggles();
    }

    async loadConfig() {
        const content = document.getElementById('main-content');
        if (!content) return;

        const configs = await this.apiCall('/config/homeassistant');
        content.innerHTML = this.renderConfig(configs);
        this.currentPage = 'config';
    }

    async loadAdmin() {
        if (this.user.role !== 'admin') {
            this.showNotification('Accès refusé', 'error');
            return;
        }

        const content = document.getElementById('main-content');
        if (!content) return;

        const [metrics, users, logs] = await Promise.all([
            this.apiCall('/admin/metrics'),
            this.apiCall('/admin/users'),
            this.apiCall('/admin/logs')
        ]);

        content.innerHTML = this.renderAdmin(metrics, users, logs);
        this.currentPage = 'admin';
    }

    async loadLogs() {
        const content = document.getElementById('main-content');
        if (!content) return;

        const logs = await this.apiCall('/admin/logs');
        content.innerHTML = this.renderLogs(logs);
        this.currentPage = 'logs';
    }

    renderDashboard(status, stats, sessions) {
        return `
            <div class="fade-in">
                <div class="header-content mb-3">
                    <h1 class="header-title">Tableau de bord</h1>
                    <div class="flex items-center gap-2">
                        <div class="status-dot ${status?.bridge?.healthy ? 'status-online' : 'status-error'}"></div>
                        <span class="text-sm">${status?.bridge?.healthy ? 'En ligne' : 'Hors ligne'}</span>
                    </div>
                </div>
                
                <div class="grid grid-cols-4 mb-3">
                    <div class="card stat-card">
                        <div class="card-content">
                            <div class="stat-value">${status?.sessions?.total || 0}</div>
                            <div class="stat-label">Sessions actives</div>
                        </div>
                    </div>
                    <div class="card stat-card">
                        <div class="card-content">
                            <div class="stat-value">${stats?.total_requests || 0}</div>
                            <div class="stat-label">Requêtes totales</div>
                        </div>
                    </div>
                    <div class="card stat-card">
                        <div class="card-content">
                            <div class="stat-value">${stats?.active_users || 0}</div>
                            <div class="stat-label">Utilisateurs actifs</div>
                        </div>
                    </div>
                    <div class="card stat-card">
                        <div class="card-content">
                            <div class="stat-value">${stats?.uptime || '0s'}</div>
                            <div class="stat-label">Uptime</div>
                        </div>
                    </div>
                </div>
                
                <div class="grid grid-cols-2">
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">Sessions récentes</h3>
                        </div>
                        <div class="card-content">
                            ${this.renderSessionsList(sessions)}
                        </div>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">Activité système</h3>
                        </div>
                        <div class="card-content">
                            <div id="activity-log">
                                Chargement des logs...
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderPermissions(permissions) {
        const tools = permissions?.data?.tools || {};

        return `
            <div class="fade-in">
                <div class="header-content mb-3">
                    <h1 class="header-title">Mes permissions</h1>
                    <button class="btn btn-secondary" onclick="dashboard.refreshPermissions()">
                        Actualiser
                    </button>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Outils Home Assistant</h3>
                        <p class="card-subtitle">Gérez vos permissions d'accès aux outils MCP</p>
                    </div>
                    <div class="card-content">
                        ${Object.keys(tools).length > 0 ?
                Object.entries(tools).map(([tool, perms]) => `
                                <div class="flex items-center justify-between p-3 border border-gray-200 rounded mb-2">
                                    <div>
                                        <div class="font-medium">${tool}</div>
                                        <div class="text-sm text-gray-500">
                                            ${perms.read ? '✅ Lecture' : '❌ Lecture'} • 
                                            ${perms.write ? '✅ Écriture' : '❌ Écriture'} • 
                                            ${perms.execute ? '✅ Exécution' : '❌ Exécution'}
                                        </div>
                                    </div>
                                    <div class="flex gap-2">
                                        <span class="badge ${perms.read ? 'badge-success' : 'badge-secondary'}">
                                            ${perms.read ? 'Lecture' : 'Pas de lecture'}
                                        </span>
                                        <span class="badge ${perms.write ? 'badge-success' : 'badge-secondary'}">
                                            ${perms.write ? 'Écriture' : 'Pas d\'écriture'}
                                        </span>
                                    </div>
                                </div>
                            `).join('') :
                '<p class="text-center text-gray-500">Aucune permission configurée</p>'
            }
                    </div>
                </div>
            </div>
        `;
    }

    renderSessionsList(sessions) {
        if (!sessions || !sessions.length) {
            return '<p class="text-center text-gray-500">Aucune session active</p>';
        }

        return sessions.slice(0, 5).map(session => `
            <div class="flex items-center justify-between p-2 border-b last:border-b-0">
                <div>
                    <div class="font-medium">${session.user_agent || 'Inconnu'}</div>
                    <div class="text-sm text-gray-500">${new Date(session.created_at).toLocaleString()}</div>
                </div>
                <span class="badge ${session.is_active ? 'badge-success' : 'badge-secondary'}">
                    ${session.is_active ? 'Active' : 'Inactive'}
                </span>
            </div>
        `).join('');
    }

    async handlePermissionToggle(event) {
        const toggle = event.target;
        const toolName = toggle.dataset.tool;
        const permissionType = toggle.dataset.permission;
        const enabled = toggle.checked;

        try {
            const response = await this.apiCall(`/permissions/tools/${toolName}`, {
                method: 'PUT',
                body: JSON.stringify({
                    [permissionType]: enabled
                })
            });

            if (response) {
                this.showNotification('Permission mise à jour', 'success');
            }
        } catch (error) {
            // Revenir à l'état précédent en cas d'erreur
            toggle.checked = !enabled;
            this.showNotification('Erreur mise à jour permission', 'error');
        }
    }

    setupPermissionToggles() {
        document.querySelectorAll('.permission-toggle').forEach(toggle => {
            toggle.addEventListener('change', (e) => this.handlePermissionToggle(e));
        });
    }

    async refreshData() {
        if (this.currentPage === 'dashboard') {
            await this.loadDashboard();
        } else if (this.currentPage === 'permissions') {
            await this.refreshPermissions();
        }
    }

    async refreshPermissions() {
        await this.loadPermissions();
    }

    updateStatus(status) {
        const statusDot = document.querySelector('.status-dot');
        if (statusDot) {
            statusDot.className = `status-dot ${status.healthy ? 'status-online' : 'status-error'}`;
        }
    }

    addLogEntry(logEntry) {
        const logContainer = document.getElementById('activity-log');
        if (logContainer) {
            const logElement = document.createElement('div');
            logElement.className = 'log-entry mb-1 p-2 bg-gray-50 rounded';
            logElement.innerHTML = `
                <div class="flex justify-between">
                    <span class="text-sm">${logEntry.message}</span>
                    <span class="text-xs text-gray-500">${new Date(logEntry.timestamp).toLocaleTimeString()}</span>
                </div>
            `;
            logContainer.insertBefore(logElement, logContainer.firstChild);

            // Garder seulement les 10 derniers logs
            const logs = logContainer.querySelectorAll('.log-entry');
            if (logs.length > 10) {
                logs[logs.length - 1].remove();
            }
        }
    }

    updateMetrics(metrics) {
        // Mettre à jour les métriques en temps réel
        Object.entries(metrics).forEach(([key, value]) => {
            const element = document.querySelector(`[data-metric="${key}"]`);
            if (element) {
                element.textContent = value;
            }
        });
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} fixed top-4 right-4 z-50 min-w-72`;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('fade-in');
        }, 10);

        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    showLoading(show) {
        const loader = document.getElementById('loader');
        if (loader) {
            loader.style.display = show ? 'block' : 'none';
        }
    }
}

// Initialiser le dashboard au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    // Vérifier si l'initialisation doit être ignorée (page de login)
    if (window.skipDashboardInit) {
        console.log('🚫 Initialisation MCPDashboard ignorée');
        return;
    }
    window.dashboard = new MCPDashboard();
});

// Gestion de l'historique du navigateur
window.addEventListener('popstate', () => {
    if (window.dashboard) {
        window.dashboard.loadCurrentPage();
    }
});

// Fonction globale pour afficher des notifications
window.showToast = function (message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-icon">${getToastIcon(type)}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.parentElement.remove()">✕</button>
        </div>
    `;

    container.appendChild(toast);

    // Animation d'entrée
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    // Suppression automatique
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, duration);
};

function getToastIcon(type) {
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    return icons[type] || 'ℹ️';
}