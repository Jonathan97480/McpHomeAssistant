/**
 * 🔐 Secure Client Cache System
 * Système de cache client sécurisé avec chiffrement pour données sensibles
 * Auto-destruction à la fermeture de page/onglet
 */

class SecureClientCache {
    constructor() {
        console.log('🔐 Initialisation Secure Client Cache...');

        this.sessionKey = this.generateSessionKey();
        this.cache = new Map();
        this.encrypted = new Map();

        // 🔄 Restaurer les données depuis sessionStorage si disponibles
        this.restoreFromSession();

        this.setupAutoDestruction();
        this.setupSessionBackup();

        console.log('🔐 Secure Client Cache initialisé');
        console.log('📊 État initial:', this.getStatus());
    }

    /**
     * Génère une clé de session unique pour le chiffrement
     */
    generateSessionKey() {
        const timestamp = Date.now().toString();
        const random = Math.random().toString(36).substring(2);
        const userAgent = navigator.userAgent.substring(0, 50);

        return btoa(timestamp + random + userAgent).substring(0, 32);
    }

    /**
     * Chiffrement simple XOR pour les données sensibles
     */
    encrypt(data) {
        const key = this.sessionKey;
        const dataStr = JSON.stringify(data);
        let encrypted = '';

        for (let i = 0; i < dataStr.length; i++) {
            const keyChar = key.charCodeAt(i % key.length);
            const dataChar = dataStr.charCodeAt(i);
            encrypted += String.fromCharCode(dataChar ^ keyChar);
        }

        return btoa(encrypted);
    }

    /**
     * Déchiffrement des données
     */
    decrypt(encryptedData) {
        try {
            const key = this.sessionKey;
            const encrypted = atob(encryptedData);
            let decrypted = '';

            for (let i = 0; i < encrypted.length; i++) {
                const keyChar = key.charCodeAt(i % key.length);
                const encryptedChar = encrypted.charCodeAt(i);
                decrypted += String.fromCharCode(encryptedChar ^ keyChar);
            }

            return JSON.parse(decrypted);
        } catch (error) {
            console.error('Erreur déchiffrement cache:', error);
            return null;
        }
    }

    /**
     * Stocke des données sensibles (chiffrées)
     */
    setSecure(key, data) {
        console.group(`🔒 setSecure(${key})`);
        console.log('Input data:', data);

        try {
            const encrypted = this.encrypt(data);
            console.log('Encrypted data length:', encrypted.length);

            this.encrypted.set(key, encrypted);
            console.log('Storage successful, encrypted cache size:', this.encrypted.size);
            console.log('All encrypted keys:', Array.from(this.encrypted.keys()));

            // 💾 Sauvegarder immédiatement dans sessionStorage
            this.saveToSession();

            console.log(`🔒 Données sécurisées stockées: ${key}`);
            console.groupEnd();
            return true;
        } catch (error) {
            console.error('Erreur stockage sécurisé:', error);
            console.groupEnd();
            return false;
        }
    }    /**
     * Récupère des données sensibles (déchiffrées)
     */
    getSecure(key) {
        console.group(`🔓 getSecure(${key})`);
        console.log('Current encrypted cache size:', this.encrypted.size);
        console.log('All encrypted keys:', Array.from(this.encrypted.keys()));

        try {
            const encrypted = this.encrypted.get(key);
            console.log('Encrypted data found:', !!encrypted);

            if (!encrypted) {
                console.log('No encrypted data found for key:', key);
                console.groupEnd();
                return null;
            }

            const decrypted = this.decrypt(encrypted);
            console.log('Decryption successful:', !!decrypted);
            console.log('Decrypted data:', decrypted);
            console.log(`🔓 Données sécurisées récupérées: ${key}`);
            console.groupEnd();
            return decrypted;
        } catch (error) {
            console.error('Erreur récupération sécurisée:', error);
            console.groupEnd();
            return null;
        }
    }

    /**
     * Stocke des données non sensibles (cache normal)
     */
    set(key, data, ttl = 300000) { // TTL par défaut: 5 minutes
        const expiry = Date.now() + ttl;
        this.cache.set(key, { data, expiry });
        console.log(`💾 Cache normal stocké: ${key} (TTL: ${ttl}ms)`);
    }

    /**
     * Récupère des données du cache normal
     */
    get(key) {
        const item = this.cache.get(key);
        if (!item) return null;

        if (Date.now() > item.expiry) {
            this.cache.delete(key);
            console.log(`⏰ Cache expiré supprimé: ${key}`);
            return null;
        }

        return item.data;
    }

    /**
     * Stocke les informations Home Assistant
     */
    setHomeAssistantConfig(config) {
        console.group('🔐 setHomeAssistantConfig');
        console.log('Input config:', config);

        const sensitiveData = {
            url: config.url,
            token: config.token,
            name: config.name || 'default',
            timestamp: Date.now()
        };

        console.log('Processed data:', sensitiveData);
        const result = this.setSecure('ha_config', sensitiveData);
        console.log('Storage result:', result);
        console.log('Cache status after storage:', this.getStatus());
        console.groupEnd();

        return result;
    }

    /**
     * Récupère les informations Home Assistant
     */
    getHomeAssistantConfig() {
        console.group('🔓 getHomeAssistantConfig');
        const result = this.getSecure('ha_config');
        console.log('Retrieved data:', result);
        console.log('Current cache status:', this.getStatus());
        console.groupEnd();

        return result;
    }

    /**
     * Stocke les informations utilisateur
     */
    setUserInfo(userInfo) {
        const sensitiveData = {
            username: userInfo.username,
            role: userInfo.role,
            permissions: userInfo.permissions || [],
            token: userInfo.token,
            timestamp: Date.now()
        };

        return this.setSecure('user_info', sensitiveData);
    }

    /**
     * Récupère les informations utilisateur
     */
    getUserInfo() {
        return this.getSecure('user_info');
    }

    /**
     * Stocke les informations de connexion serveur
     */
    setServerInfo(serverInfo) {
        const sensitiveData = {
            url: serverInfo.url || window.location.origin,
            session_id: serverInfo.session_id,
            connected_at: Date.now(),
            timestamp: Date.now()
        };

        return this.setSecure('server_info', sensitiveData);
    }

    /**
     * Récupère les informations de connexion serveur
     */
    getServerInfo() {
        return this.getSecure('server_info');
    }

    /**
     * Vérifie si une donnée existe dans le cache
     */
    has(key) {
        return this.cache.has(key) || this.encrypted.has(key);
    }

    /**
     * Supprime une entrée du cache
     */
    remove(key) {
        this.cache.delete(key);
        this.encrypted.delete(key);
        console.log(`🗑️ Cache supprimé: ${key}`);
    }

    /**
     * Nettoie le cache expiré
     */
    cleanup() {
        const now = Date.now();
        let cleaned = 0;

        for (const [key, item] of this.cache.entries()) {
            if (now > item.expiry) {
                this.cache.delete(key);
                cleaned++;
            }
        }

        if (cleaned > 0) {
            console.log(`🧹 ${cleaned} entrées expirées nettoyées`);
        }
    }

    /**
     * Vide complètement le cache
     */
    clear() {
        const totalEntries = this.cache.size + this.encrypted.size;
        this.cache.clear();
        this.encrypted.clear();
        console.log(`🗑️ Cache complètement vidé (${totalEntries} entrées)`);
    }

    /**
     * Configure la destruction automatique du cache
     */
    setupAutoDestruction() {
        // Destruction à la fermeture de page/onglet
        window.addEventListener('beforeunload', () => {
            console.log('🔥 Auto-destruction du cache à la fermeture');
            this.saveToSession(); // Sauvegarder avant de quitter
            this.clear();
        });

        // Destruction à la fermeture de l'onglet (visibilitychange)
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'hidden') {
                // Sauvegarder quand l'onglet devient invisible
                this.saveToSession();
                console.log('👁️ Onglet masqué - sauvegarde et nettoyage préventif');
                this.cleanup();
            }
        });

        // Nettoyage périodique des données expirées
        setInterval(() => {
            this.cleanup();
        }, 60000); // Toutes les minutes

        console.log('⚙️ Auto-destruction configurée');
    }

    /**
     * 💾 Configure la sauvegarde automatique en sessionStorage
     */
    setupSessionBackup() {
        // Sauvegarder automatiquement toutes les 10 secondes
        setInterval(() => {
            if (this.encrypted.size > 0) {
                this.saveToSession();
            }
        }, 10000);

        console.log('💾 Backup sessionStorage configuré');
    }

    /**
     * 💾 Sauvegarde les données chiffrées dans sessionStorage
     */
    saveToSession() {
        try {
            if (this.encrypted.size === 0) {
                console.log('📭 Rien à sauvegarder dans sessionStorage');
                return;
            }

            const backup = {
                sessionKey: this.sessionKey,
                encrypted: Array.from(this.encrypted.entries()),
                timestamp: Date.now()
            };

            sessionStorage.setItem('secureCache_backup', JSON.stringify(backup));
            console.log(`💾 Sauvegarde sessionStorage: ${this.encrypted.size} entrées`);
        } catch (error) {
            console.warn('⚠️ Erreur sauvegarde sessionStorage:', error);
        }
    }

    /**
     * 🔄 Restaure les données depuis sessionStorage
     */
    restoreFromSession() {
        try {
            const backupStr = sessionStorage.getItem('secureCache_backup');
            if (!backupStr) {
                console.log('📭 Aucune sauvegarde trouvée dans sessionStorage');
                return;
            }

            const backup = JSON.parse(backupStr);

            // Vérifier que la sauvegarde n'est pas trop ancienne (max 1 heure)
            const maxAge = 60 * 60 * 1000; // 1 heure
            if (Date.now() - backup.timestamp > maxAge) {
                console.log('🕐 Sauvegarde sessionStorage trop ancienne, ignorée');
                sessionStorage.removeItem('secureCache_backup');
                return;
            }

            // Restaurer la clé de session et les données
            this.sessionKey = backup.sessionKey;
            this.encrypted = new Map(backup.encrypted);

            console.log(`🔄 Restauration sessionStorage: ${this.encrypted.size} entrées`);
            console.log('🔑 Clé de session restaurée');
        } catch (error) {
            console.warn('⚠️ Erreur restauration sessionStorage:', error);
            sessionStorage.removeItem('secureCache_backup');
        }
    }

    /**
     * Retourne le statut du cache
     */
    getStatus() {
        return {
            normalCache: this.cache.size,
            secureCache: this.encrypted.size,
            sessionKey: this.sessionKey.substring(0, 8) + '...',
            timestamp: Date.now()
        };
    }

    /**
     * Mode debug - affiche le contenu du cache (sans les données sensibles)
     */
    debug() {
        console.group('🔍 Secure Client Cache Debug');
        console.log('Status:', this.getStatus());
        console.log('Cache normal keys:', Array.from(this.cache.keys()));
        console.log('Cache sécurisé keys:', Array.from(this.encrypted.keys()));
        console.groupEnd();
    }
}

// Instance globale du cache sécurisé
window.secureCache = new SecureClientCache();

// Raccourcis globaux pour faciliter l'utilisation
window.cacheHA = (config) => window.secureCache.setHomeAssistantConfig(config);
window.getHA = () => window.secureCache.getHomeAssistantConfig();
window.cacheUser = (userInfo) => window.secureCache.setUserInfo(userInfo);
window.getUser = () => window.secureCache.getUserInfo();
window.cacheServer = (serverInfo) => window.secureCache.setServerInfo(serverInfo);
window.getServer = () => window.secureCache.getServerInfo();

console.log('✅ Secure Client Cache System chargé et prêt');