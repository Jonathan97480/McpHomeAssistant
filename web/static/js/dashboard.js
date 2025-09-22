// 🚀 HTTP-MCP Bridge Dashboard - JavaScript principal
// Gestion de l'interface utilisateur, API calls et interactivité

class MCPDashboard {
    constructor() {
        this.baseUrl = window.location.origin;

        // 🔐 Utilisation du cache sécurisé pour les données sensibles
        this.initSecureData();

        this.socket = null;
        this.currentPage = 'dashboard';

        this.init();
    }

    /**
     * 🔐 Initialise les données depuis le cache sécurisé
     */
    initSecureData() {
        // Récupérer depuis le cache sécurisé en priorité
        const cachedUser = window.secureCache ? window.getUser() : null;
        const cachedServer = window.secureCache ? window.getServer() : null;

        if (cachedUser) {
            this.token = cachedUser.token;
            this.user = cachedUser;
            console.log('🔓 Données utilisateur récupérées du cache sécurisé');
        } else {
            // Fallback vers localStorage (migration progressive)
            this.token = localStorage.getItem('mcp_token');
            this.user = JSON.parse(localStorage.getItem('mcp_user') || '{}');

            // Migrer vers le cache sécurisé si possible
            if (this.user.username && window.secureCache) {
                this.user.token = this.token;
                window.cacheUser(this.user);
                console.log('🔄 Migration utilisateur vers cache sécurisé');
            }
        }

        if (cachedServer) {
            console.log('🔓 Infos serveur récupérées du cache sécurisé');
        }
    }

    init() {
        console.log('🚀 Initialisation MCP Dashboard');

        // Ne pas initialiser sur les pages d'authentification
        const currentPath = window.location.pathname;
        if (currentPath === '/login' || currentPath === '/register') {
            console.log('📍 Page d\'authentification détectée, initialisation des événements uniquement');
            this.setupAuthEventListeners();
            return;
        }

        // Vérifier l'authentification pour les pages protégées
        if (!this.token) {
            console.log('🔒 Aucun token trouvé, redirection vers login');
            // Petite temporisation pour éviter les redirections immédiates
            setTimeout(() => this.redirectToLogin(), 100);
            return;
        }

        // Valider le token avant de continuer
        this.validateToken().then(isValid => {
            if (!isValid) {
                console.log('🔒 Token invalide, redirection vers login');
                this.clearAuthData();
                // Petite temporisation pour éviter les redirections immédiates
                setTimeout(() => this.redirectToLogin(), 100);
                return;
            }

            console.log('✅ Token valide, initialisation complète du dashboard');

            // Initialiser l'interface
            this.setupEventListeners();
            this.setupNavigation();
            this.setupWebSocket();

            // Charger la page actuelle
            this.loadCurrentPage();

            // Actualiser les données toutes les 30 secondes
            setInterval(() => this.refreshData(), 30000);
        }).catch(error => {
            console.error('❌ Erreur validation token:', error);
            this.clearAuthData();
            this.redirectToLogin();
        });
    }

    /**
     * 🔐 Configuration des événements pour les pages d'authentification uniquement
     */
    setupAuthEventListeners() {
        console.log('🔐 Configuration des événements d\'authentification');

        // Formulaire de connexion
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Formulaire d'inscription
        const registerForm = document.getElementById('register-form');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }

        // Liens de navigation entre login/register
        document.querySelectorAll('a[href="/login"], a[href="/register"]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                window.location.href = link.getAttribute('href');
            });
        });
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

        // Formulaires (aussi configuré dans setupAuthEventListeners)
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
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.warn('Message WebSocket non-JSON reçu:', event.data);
                    // Traiter comme message texte simple
                    this.handleWebSocketMessage({
                        type: 'text',
                        message: event.data,
                        timestamp: Date.now()
                    });
                }
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
                    // Ne pas rediriger automatiquement pour certains endpoints
                    if (!options.skipAutoRedirect) {
                        this.redirectToLogin();
                    }
                    return null;
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`❌ Erreur API ${endpoint}:`, error);
            if (!options.skipNotification) {
                this.showNotification('Erreur de connexion', 'error');
            }
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

        // 🔐 Nettoyage sécurisé de toutes les données sensibles
        if (window.secureCache) {
            window.secureCache.clear();
            console.log('🔥 Cache sécurisé vidé à la déconnexion');
        }

        // Nettoyage localStorage (migration progressive)
        localStorage.removeItem('mcp_token');
        localStorage.removeItem('mcp_user');
        localStorage.removeItem('ha_config');  // Au cas où
        sessionStorage.clear();

        if (this.socket) {
            this.socket.close();
        }

        this.redirectToLogin();
    }

    redirectToLogin() {
        // Éviter les redirections en boucle
        if (window.location.pathname === '/login') {
            console.log('🔄 Déjà sur la page login, éviter la redirection');
            return;
        }
        console.log('🔀 Redirection vers login');
        window.location.href = '/login';
    }

    /**
     * 🔐 Valide le token auprès du serveur
     */
    async validateToken() {
        if (!this.token) return false;

        try {
            const response = await fetch('/auth/me', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });
            return response.ok;
        } catch (error) {
            console.error('❌ Erreur validation token:', error);
            return false;
        }
    }

    /**
     * 🗑️ Nettoie toutes les données d'authentification
     */
    clearAuthData() {
        // Nettoyer localStorage
        localStorage.removeItem('mcp_token');
        localStorage.removeItem('mcp_user');

        // Nettoyer cache sécurisé
        if (window.secureCache) {
            window.secureCache.clear();
        }

        // Réinitialiser les propriétés
        this.token = null;
        this.user = {};

        console.log('🗑️ Données d\'authentification supprimées');
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

            // Charger les données spécifiques à la page
            await this.loadPageData(path);

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
            // Créer un identifiant unique pour ce script basé sur son contenu
            const scriptContent = script.textContent || script.src || '';
            const scriptId = this.generateScriptId(scriptContent);

            // Vérifier si ce script a déjà été exécuté
            if (!this.executedScripts) {
                this.executedScripts = new Set();
            }

            // Pages qui doivent réexécuter leurs scripts pour recharger les données
            const currentPath = window.location.pathname;
            const reloadablePages = ['/tools', '/permissions', '/overview', '/config', '/logs'];
            const shouldReexecute = reloadablePages.some(path => currentPath.includes(path));

            if (!shouldReexecute && this.executedScripts.has(scriptId)) {
                console.log(`Script déjà exécuté, ignore`);
                return;
            }

            try {
                if (script.src) {
                    // Script externe - vérifier s'il n'est pas déjà chargé
                    const existingScript = document.querySelector(`script[src="${script.src}"]`);
                    if (existingScript) {
                        console.log(`Script externe ${script.src} déjà chargé`);
                        return;
                    }
                    const newScript = document.createElement('script');
                    newScript.src = script.src;
                    document.head.appendChild(newScript);
                } else if (script.textContent) {
                    // Script inline - l'exécuter dans un scope isolé
                    try {
                        // Utiliser une fonction pour créer un scope local
                        const func = new Function(script.textContent);
                        func();
                    } catch (evalError) {
                        // Si l'exécution directe échoue, essayer avec eval
                        console.log('Tentative avec eval...', evalError.message);
                        eval(script.textContent);
                    }
                }

                // Marquer ce script comme exécuté
                this.executedScripts.add(scriptId);

            } catch (error) {
                console.error('Erreur lors de l\'exécution du script:', error);
                // Ne pas bloquer l'exécution des autres scripts
            }
        });
    }

    generateScriptId(content) {
        // Générer un identifiant sécurisé sans utiliser btoa pour éviter les erreurs Unicode
        try {
            // Nettoyer le contenu pour ne garder que les caractères ASCII
            const cleanContent = content.substring(0, 100).replace(/[^\x00-\x7F]/g, "");

            // Utiliser une méthode alternative pour générer l'ID
            let hash = 0;
            for (let i = 0; i < cleanContent.length; i++) {
                const char = cleanContent.charCodeAt(i);
                hash = ((hash << 5) - hash) + char;
                hash = hash & hash; // Convertir en 32bit integer
            }

            return 'script_' + Math.abs(hash).toString(36);
        } catch (error) {
            console.warn('Erreur génération ID script:', error);
            // Fallback: utiliser timestamp
            return 'script_' + Date.now().toString(36);
        }
    }

    async loadCurrentPage() {
        const path = window.location.pathname;
        await this.loadPage(path);
    }

    async loadDashboard() {
        const content = document.getElementById('main-content');
        if (!content) return;

        // Charger les métriques du dashboard
        const [status, stats, metrics] = await Promise.all([
            this.apiCall('/mcp/status'),
            this.apiCall('/admin/stats'),
            this.apiCall('/api/metrics')
        ]);

        // Récupérer les sessions de manière sécurisée
        let sessions = [];
        try {
            const sessionsResponse = await this.apiCall('/auth/sessions', {
                skipAutoRedirect: true,
                skipNotification: true
            });
            sessions = sessionsResponse?.sessions || [];
        } catch (error) {
            console.warn('⚠️ Impossible de récupérer les sessions:', error);
            sessions = []; // Valeur par défaut
        }

        content.innerHTML = this.renderDashboard(status, stats, metrics, sessions);
        this.currentPage = 'dashboard';
    }

    async loadPermissions() {
        const content = document.getElementById('main-content');
        if (!content) return;

        // Utiliser le bon endpoint API
        const response = await fetch('/api/permissions');
        const data = await response.json();
        const permissions = data.permissions || [];

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

        const logs = await this.apiCall('/api/logs');
        content.innerHTML = this.renderLogs(logs);
        this.currentPage = 'logs';
    }

    async loadPageData(path) {
        try {
            switch (path) {
                case '/tools':
                    await this.loadTools();
                    break;
                case '/logs':
                    await this.loadLogsData();
                    break;
                // Ajouter d'autres pages spéciales si nécessaire
                default:
                    break;
            }
        } catch (error) {
            console.error('Erreur lors du chargement des données de la page:', error);
        }
    }

    async loadTools() {
        console.log('🔧 Chargement des outils MCP...');

        try {
            // Initialiser une session MCP d'abord
            const mcpSession = await this.initializeMCPSession();

            if (mcpSession && mcpSession.session_id) {
                // Charger la liste des outils avec la session
                const tools = await this.getMCPTools(mcpSession.session_id);

                // Mettre à jour l'interface avec les outils
                this.updateToolsInterface(tools);

                // Configurer les event listeners pour les outils
                this.setupToolsEventListeners();
            } else {
                // Fallback: utiliser l'API tools qui retourne des données d'exemple
                const tools = await this.apiCall('/api/tools');
                this.updateToolsInterface(tools);
                this.setupToolsEventListeners();
            }
        } catch (error) {
            console.error('❌ Erreur lors du chargement des outils MCP:', error);
            this.showNotification('Erreur lors du chargement des outils MCP', 'error');

            // Afficher une interface vide avec message d'erreur
            this.updateToolsInterface([]);
        }
    }

    async initializeMCPSession() {
        try {
            const response = await this.apiCall('/mcp/initialize', {
                method: 'POST',
                body: JSON.stringify({
                    serverName: 'home-assistant',
                    client_info: {
                        name: 'web-interface',
                        version: '1.0.0'
                    }
                })
            });

            if (response && response.result) {
                return response.result;
            }
        } catch (error) {
            console.warn('⚠️ Impossible d\'initialiser la session MCP:', error);
        }
        return null;
    }

    async getMCPTools(sessionId) {
        try {
            const response = await this.apiCall('/mcp/tools/list', {
                method: 'POST',
                headers: {
                    'X-Session-ID': sessionId
                },
                body: JSON.stringify({})
            });

            if (response && response.result && response.result.tools) {
                return response.result.tools;
            }
        } catch (error) {
            console.warn('⚠️ Impossible de récupérer les outils MCP:', error);
        }
        return [];
    }

    updateToolsInterface(tools) {
        // Mettre à jour les statistiques
        const totalCount = tools.length;
        const activeCount = tools.filter(tool => tool.status !== 'inactive').length;
        const totalUsage = tools.reduce((sum, tool) => sum + (tool.usage_count || 0), 0);
        const avgResponseTime = tools.length > 0 ?
            Math.round(tools.reduce((sum, tool) => sum + (tool.avg_response_time || 0), 0) / tools.length) : 0;

        // Mettre à jour les éléments du DOM
        const updateElement = (id, value) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        };

        updateElement('total-tools-count', totalCount);
        updateElement('active-tools-count', activeCount);
        updateElement('total-usage-count', totalUsage);
        updateElement('avg-response-time', `${avgResponseTime}ms`);

        // Mettre à jour la liste des outils
        const toolsList = document.getElementById('tools-list');
        if (toolsList) {
            if (tools.length === 0) {
                toolsList.innerHTML = `
                    <div class="card">
                        <div class="card-body text-center py-8">
                            <div class="text-6xl mb-4">🔧</div>
                            <h3 class="text-xl font-semibold mb-2">Aucun outil disponible</h3>
                            <p class="text-secondary">Les outils MCP seront affichés ici une fois configurés.</p>
                        </div>
                    </div>
                `;
            } else {
                toolsList.innerHTML = tools.map(tool => this.renderToolCard(tool)).join('');
            }
        }
    }

    renderToolCard(tool) {
        const statusClass = {
            'active': 'text-green-600',
            'inactive': 'text-gray-500',
            'error': 'text-red-600'
        }[tool.status] || 'text-gray-500';

        const statusIcon = {
            'active': '✅',
            'inactive': '⏸️',
            'error': '❌'
        }[tool.status] || '❓';

        return `
            <div class="card mb-4 tool-card" data-tool-id="${tool.name || tool.id}">
                <div class="card-body">
                    <div class="flex justify-between items-start mb-3">
                        <div>
                            <h4 class="text-lg font-semibold">${tool.name || tool.id}</h4>
                            <p class="text-secondary text-sm">${tool.description || 'Aucune description'}</p>
                        </div>
                        <div class="flex items-center gap-2">
                            <span class="${statusClass}">${statusIcon}</span>
                            <button class="btn btn-sm btn-primary" onclick="dashboard.testTool('${tool.name || tool.id}')">
                                🧪 Tester
                            </button>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-3 gap-4 text-sm">
                        <div>
                            <span class="text-secondary">Catégorie:</span>
                            <span class="ml-1">${tool.category || 'général'}</span>
                        </div>
                        <div>
                            <span class="text-secondary">Utilisations:</span>
                            <span class="ml-1">${tool.usage_count || 0}</span>
                        </div>
                        <div>
                            <span class="text-secondary">Dernière utilisation:</span>
                            <span class="ml-1">${tool.last_used ? new Date(tool.last_used).toLocaleDateString() : 'Jamais'}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    setupToolsEventListeners() {
        // Bouton actualiser
        const refreshBtn = document.getElementById('refresh-tools');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadTools());
        }

        // Bouton tester tout
        const testAllBtn = document.getElementById('test-all-tools');
        if (testAllBtn) {
            testAllBtn.addEventListener('click', () => this.testAllTools());
        }

        // Recherche et filtres
        const searchInput = document.getElementById('search-tools');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.filterTools());
        }

        const categoryFilter = document.getElementById('filter-category');
        if (categoryFilter) {
            categoryFilter.addEventListener('change', () => this.filterTools());
        }

        const statusFilter = document.getElementById('filter-status');
        if (statusFilter) {
            statusFilter.addEventListener('change', () => this.filterTools());
        }

        const clearFiltersBtn = document.getElementById('clear-filters');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => this.clearToolsFilters());
        }
    }

    filterTools() {
        const searchTerm = document.getElementById('search-tools')?.value.toLowerCase() || '';
        const categoryFilter = document.getElementById('filter-category')?.value || '';
        const statusFilter = document.getElementById('filter-status')?.value || '';

        const toolCards = document.querySelectorAll('.tool-card');

        toolCards.forEach(card => {
            const toolName = card.querySelector('h4').textContent.toLowerCase();
            const toolDescription = card.querySelector('p').textContent.toLowerCase();
            const toolCategory = card.querySelector('.text-secondary').textContent.toLowerCase();

            const matchesSearch = searchTerm === '' ||
                toolName.includes(searchTerm) ||
                toolDescription.includes(searchTerm);

            const matchesCategory = categoryFilter === '' || toolCategory.includes(categoryFilter);

            // Le statut est plus complexe à extraire, on le simplifie pour cet exemple
            const matchesStatus = statusFilter === '';

            if (matchesSearch && matchesCategory && matchesStatus) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }

    clearToolsFilters() {
        document.getElementById('search-tools').value = '';
        document.getElementById('filter-category').value = '';
        document.getElementById('filter-status').value = '';
        this.filterTools();
    }

    async testTool(toolId) {
        console.log(`🧪 Test de l'outil: ${toolId}`);
        this.showNotification(`Test de l'outil ${toolId} lancé`, 'info');
        // TODO: Implémenter le test d'outil
    }

    async testAllTools() {
        console.log('🧪 Test de tous les outils');
        this.showNotification('Test de tous les outils lancé', 'info');
        // TODO: Implémenter le test de tous les outils
    }

    async loadLogsData() {
        console.log('📄 Chargement des logs...');

        try {
            // Récupérer les logs via l'API
            const logsResponse = await this.apiCall('/api/logs');

            if (logsResponse && logsResponse.logs) {
                // Mettre à jour les statistiques des logs
                this.updateLogsStats(logsResponse.stats || {});

                // Mettre à jour la liste des logs
                this.updateLogsList(logsResponse.logs);

                // Configurer les event listeners pour les logs
                this.setupLogsEventListeners();
            } else {
                console.warn('⚠️ Aucun log récupéré');
                this.updateLogsStats({});
                this.updateLogsList([]);
            }
        } catch (error) {
            console.error('❌ Erreur lors du chargement des logs:', error);
            this.showNotification('Erreur lors du chargement des logs', 'error');

            // Afficher une interface vide avec message d'erreur
            this.updateLogsStats({});
            this.updateLogsList([]);
        }
    }

    updateLogsStats(stats) {
        // Mettre à jour les statistiques des logs
        const updateElement = (id, value) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        };

        updateElement('total-logs-count', stats.total_logs || 0);
        updateElement('error-logs-count', stats.errors || 0);
        updateElement('warning-logs-count', stats.warnings || 0);
        updateElement('logs-size-mb', stats.size_mb ? `${stats.size_mb} MB` : '0 MB');
    }

    updateLogsList(logs) {
        const logsList = document.getElementById('logs-list');
        if (!logsList) return;

        if (logs.length === 0) {
            logsList.innerHTML = `
                <div class="card">
                    <div class="card-body text-center py-8">
                        <div class="text-6xl mb-4">📄</div>
                        <h3 class="text-xl font-semibold mb-2">Aucun log disponible</h3>
                        <p class="text-secondary">Les logs système apparaîtront ici.</p>
                    </div>
                </div>
            `;
        } else {
            logsList.innerHTML = logs.map(log => this.renderLogEntry(log)).join('');
        }
    }

    renderLogEntry(log) {
        const levelClass = {
            'ERROR': 'text-red-600 bg-red-50',
            'WARNING': 'text-yellow-600 bg-yellow-50',
            'INFO': 'text-blue-600 bg-blue-50',
            'DEBUG': 'text-gray-600 bg-gray-50'
        }[log.level] || 'text-gray-600 bg-gray-50';

        const levelIcon = {
            'ERROR': '❌',
            'WARNING': '⚠️',
            'INFO': 'ℹ️',
            'DEBUG': '🔍'
        }[log.level] || 'ℹ️';

        return `
            <div class="card mb-2 log-entry" data-level="${log.level}" data-category="${log.category}">
                <div class="card-body py-3">
                    <div class="flex justify-between items-start">
                        <div class="flex items-start gap-3 flex-1">
                            <span class="text-lg">${levelIcon}</span>
                            <div class="flex-1">
                                <div class="flex items-center gap-2 mb-1">
                                    <span class="px-2 py-1 rounded text-xs font-medium ${levelClass}">
                                        ${log.level}
                                    </span>
                                    <span class="text-xs text-secondary">${log.category}</span>
                                    <span class="text-xs text-secondary">${this.formatLogTimestamp(log.timestamp)}</span>
                                </div>
                                <p class="text-sm">${log.message}</p>
                                ${log.details && log.details !== log.message ? `
                                    <details class="mt-2">
                                        <summary class="text-xs text-secondary cursor-pointer">Détails</summary>
                                        <pre class="text-xs bg-gray-100 p-2 rounded mt-1 overflow-x-auto">${log.details}</pre>
                                    </details>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    formatLogTimestamp(timestamp) {
        try {
            const date = new Date(timestamp);
            return date.toLocaleString('fr-FR', {
                day: '2-digit',
                month: '2-digit',
                year: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        } catch {
            return timestamp;
        }
    }

    setupLogsEventListeners() {
        // Bouton actualiser
        const refreshBtn = document.getElementById('refresh-logs');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadLogsData());
        }

        // Bouton effacer
        const clearBtn = document.getElementById('clear-logs');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearLogs());
        }

        // Filtres de logs
        const levelFilter = document.getElementById('filter-log-level');
        if (levelFilter) {
            levelFilter.addEventListener('change', () => this.filterLogs());
        }

        const categoryFilter = document.getElementById('filter-log-category');
        if (categoryFilter) {
            categoryFilter.addEventListener('change', () => this.filterLogs());
        }

        const searchInput = document.getElementById('search-logs');
        if (searchInput) {
            searchInput.addEventListener('input', () => this.filterLogs());
        }
    }

    filterLogs() {
        const levelFilter = document.getElementById('filter-log-level')?.value || '';
        const categoryFilter = document.getElementById('filter-log-category')?.value || '';
        const searchTerm = document.getElementById('search-logs')?.value.toLowerCase() || '';

        const logEntries = document.querySelectorAll('.log-entry');

        logEntries.forEach(entry => {
            const level = entry.dataset.level;
            const category = entry.dataset.category;
            const text = entry.textContent.toLowerCase();

            const matchesLevel = levelFilter === '' || level === levelFilter;
            const matchesCategory = categoryFilter === '' || category.includes(categoryFilter);
            const matchesSearch = searchTerm === '' || text.includes(searchTerm);

            if (matchesLevel && matchesCategory && matchesSearch) {
                entry.style.display = 'block';
            } else {
                entry.style.display = 'none';
            }
        });
    }

    async clearLogs() {
        if (confirm('Êtes-vous sûr de vouloir effacer tous les logs ?')) {
            try {
                await this.apiCall('/api/logs/clear', { method: 'DELETE' });
                this.showNotification('Logs effacés avec succès', 'success');
                await this.loadLogsData();
            } catch (error) {
                console.error('❌ Erreur lors de l\'effacement des logs:', error);
                this.showNotification('Erreur lors de l\'effacement des logs', 'error');
            }
        }
    }

    renderDashboard(status, stats, metrics, sessions = []) {
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
                            <div class="stat-value">${metrics?.active_connections || 0}</div>
                            <div class="stat-label">Sessions actives</div>
                        </div>
                    </div>
                    <div class="card stat-card">
                        <div class="card-content">
                            <div class="stat-value">${stats?.data?.requests?.total_requests || 0}</div>
                            <div class="stat-label">Requêtes totales</div>
                        </div>
                    </div>
                    <div class="card stat-card">
                        <div class="card-content">
                            <div class="stat-value">${stats?.data?.requests?.unique_sessions || 0}</div>
                            <div class="stat-label">Utilisateurs actifs</div>
                        </div>
                    </div>
                    <div class="card stat-card">
                        <div class="card-content">
                            <div class="stat-value">${metrics?.uptime ? this.formatUptime(metrics.uptime) : '0s'}</div>
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

    /**
     * 🕐 Formate l'uptime en secondes vers un format lisible
     */
    formatUptime(seconds) {
        if (seconds < 60) return `${seconds}s`;
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
        return `${Math.floor(seconds / 86400)}j`;
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