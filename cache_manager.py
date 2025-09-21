"""
Module de gestion du cache L1 mémoire et du circuit breaker
pour optimiser les performances du bridge HTTP-MCP.
"""

import asyncio
import time
from typing import Any, Dict, Optional, Tuple
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
import logging
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """États du circuit breaker"""
    CLOSED = "closed"      # Fonctionnement normal
    OPEN = "open"          # Circuit ouvert (erreurs détectées)
    HALF_OPEN = "half_open"  # Test de récupération

@dataclass
class CacheEntry:
    """Entrée du cache avec métadonnées"""
    value: Any
    timestamp: float
    ttl: float
    hit_count: int = 0
    
    @property
    def is_expired(self) -> bool:
        """Vérifie si l'entrée est expirée"""
        return time.time() > self.timestamp + self.ttl
    
    @property
    def age_seconds(self) -> float:
        """Retourne l'âge en secondes"""
        return time.time() - self.timestamp

@dataclass
class CircuitBreakerConfig:
    """Configuration du circuit breaker"""
    failure_threshold: int = 5  # Seuil d'erreurs avant ouverture
    recovery_timeout: float = 30.0  # Timeout avant test de récupération
    success_threshold: int = 3  # Succès requis pour fermeture
    timeout: float = 10.0  # Timeout des requêtes

@dataclass
class CircuitBreakerStats:
    """Statistiques du circuit breaker"""
    state: CircuitState
    failure_count: int
    success_count: int
    last_failure_time: Optional[float]
    last_success_time: Optional[float]
    state_change_time: float
    total_requests: int
    successful_requests: int

class LRUCache:
    """Cache LRU (Least Recently Used) thread-safe"""
    
    def __init__(self, max_size: int = 1000, default_ttl: float = 300.0):
        """
        Initialise le cache LRU
        
        Args:
            max_size: Taille maximale du cache
            default_ttl: TTL par défaut en secondes (5 minutes)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = asyncio.Lock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired': 0,
            'size': 0
        }
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Récupère une valeur du cache
        
        Args:
            key: Clé de l'entrée
            
        Returns:
            Valeur si trouvée et non expirée, None sinon
        """
        async with self._lock:
            if key not in self._cache:
                self._stats['misses'] += 1
                return None
            
            entry = self._cache[key]
            
            # Vérifier l'expiration
            if entry.is_expired:
                del self._cache[key]
                self._stats['expired'] += 1
                self._stats['misses'] += 1
                self._stats['size'] = len(self._cache)
                return None
            
            # Déplacer en fin (plus récent)
            self._cache.move_to_end(key)
            entry.hit_count += 1
            self._stats['hits'] += 1
            
            logger.debug(f"Cache HIT: {key} (age: {entry.age_seconds:.1f}s, hits: {entry.hit_count})")
            return entry.value
    
    async def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """
        Ajoute une valeur au cache
        
        Args:
            key: Clé de l'entrée
            value: Valeur à stocker
            ttl: Durée de vie en secondes (utilise default_ttl si None)
        """
        async with self._lock:
            ttl = ttl or self.default_ttl
            
            # Créer nouvelle entrée
            entry = CacheEntry(
                value=value,
                timestamp=time.time(),
                ttl=ttl
            )
            
            # Ajouter/Mettre à jour
            if key in self._cache:
                self._cache[key] = entry
                self._cache.move_to_end(key)
            else:
                self._cache[key] = entry
                self._stats['size'] = len(self._cache)
                
                # Éviction si nécessaire
                if len(self._cache) > self.max_size:
                    oldest_key = next(iter(self._cache))
                    del self._cache[oldest_key]
                    self._stats['evictions'] += 1
                    self._stats['size'] = len(self._cache)
            
            logger.debug(f"Cache SET: {key} (ttl: {ttl}s)")
    
    async def delete(self, key: str) -> bool:
        """
        Supprime une entrée du cache
        
        Args:
            key: Clé à supprimer
            
        Returns:
            True si supprimée, False si non trouvée
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats['size'] = len(self._cache)
                logger.debug(f"Cache DELETE: {key}")
                return True
            return False
    
    async def clear(self) -> None:
        """Vide le cache"""
        async with self._lock:
            cleared_count = len(self._cache)
            self._cache.clear()
            self._stats['size'] = 0
            logger.info(f"Cache cleared: {cleared_count} entries removed")
    
    async def cleanup_expired(self) -> int:
        """
        Nettoie les entrées expirées
        
        Returns:
            Nombre d'entrées supprimées
        """
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                self._stats['expired'] += len(expired_keys)
                self._stats['size'] = len(self._cache)
                logger.debug(f"Cache cleanup: {len(expired_keys)} expired entries removed")
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache"""
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self._stats,
            'total_requests': total_requests,
            'hit_rate_percent': round(hit_rate, 2),
            'max_size': self.max_size,
            'default_ttl': self.default_ttl
        }

class CircuitBreaker:
    """Circuit breaker pour protéger contre les pannes externes"""
    
    def __init__(self, config: CircuitBreakerConfig):
        """
        Initialise le circuit breaker
        
        Args:
            config: Configuration du circuit breaker
        """
        self.config = config
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._last_success_time: Optional[float] = None
        self._state_change_time = time.time()
        self._total_requests = 0
        self._successful_requests = 0
        self._lock = asyncio.Lock()
    
    async def call(self, coro_func, *args, **kwargs) -> Any:
        """
        Exécute une fonction asynchrone protégée par le circuit breaker
        
        Args:
            coro_func: Fonction coroutine à exécuter
            *args, **kwargs: Arguments de la fonction
            
        Returns:
            Résultat de la fonction
            
        Raises:
            CircuitBreakerOpenError: Si le circuit est ouvert
            TimeoutError: Si timeout dépassé
            Exception: Erreur de la fonction appelée
        """
        async with self._lock:
            self._total_requests += 1
            
            # Vérifier l'état du circuit
            if self._state == CircuitState.OPEN:
                # Vérifier si on peut passer en half-open
                if (self._last_failure_time and 
                    time.time() - self._last_failure_time >= self.config.recovery_timeout):
                    logger.info("Circuit breaker: Transition OPEN -> HALF_OPEN")
                    self._state = CircuitState.HALF_OPEN
                    self._state_change_time = time.time()
                else:
                    raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        try:
            # Exécuter avec timeout
            result = await asyncio.wait_for(
                coro_func(*args, **kwargs),
                timeout=self.config.timeout
            )
            
            await self._on_success()
            return result
            
        except Exception as e:
            await self._on_failure()
            raise
    
    async def _on_success(self) -> None:
        """Traite un succès"""
        async with self._lock:
            self._successful_requests += 1
            self._last_success_time = time.time()
            
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    logger.info("Circuit breaker: Transition HALF_OPEN -> CLOSED")
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._success_count = 0
                    self._state_change_time = time.time()
            elif self._state == CircuitState.CLOSED:
                # Reset failure count on success
                self._failure_count = 0
    
    async def _on_failure(self) -> None:
        """Traite un échec"""
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            if self._state == CircuitState.CLOSED:
                if self._failure_count >= self.config.failure_threshold:
                    logger.warning(f"Circuit breaker: Transition CLOSED -> OPEN after {self._failure_count} failures")
                    self._state = CircuitState.OPEN
                    self._state_change_time = time.time()
            elif self._state == CircuitState.HALF_OPEN:
                logger.warning("Circuit breaker: Transition HALF_OPEN -> OPEN")
                self._state = CircuitState.OPEN
                self._success_count = 0
                self._state_change_time = time.time()
    
    def get_stats(self) -> CircuitBreakerStats:
        """Retourne les statistiques du circuit breaker"""
        return CircuitBreakerStats(
            state=self._state,
            failure_count=self._failure_count,
            success_count=self._success_count,
            last_failure_time=self._last_failure_time,
            last_success_time=self._last_success_time,
            state_change_time=self._state_change_time,
            total_requests=self._total_requests,
            successful_requests=self._successful_requests
        )
    
    @property
    def state(self) -> CircuitState:
        """État actuel du circuit"""
        return self._state
    
    @property
    def is_available(self) -> bool:
        """Indique si le circuit est disponible"""
        if self._state == CircuitState.OPEN:
            # Vérifier si on peut passer en half-open
            if (self._last_failure_time and 
                time.time() - self._last_failure_time >= self.config.recovery_timeout):
                return True
            return False
        return True

class CircuitBreakerOpenError(Exception):
    """Exception levée quand le circuit breaker est ouvert"""
    pass

class CacheManager:
    """Gestionnaire central du cache et du circuit breaker"""
    
    def __init__(self, 
                 cache_size: int = 1000,
                 cache_ttl: float = 300.0,
                 circuit_config: Optional[CircuitBreakerConfig] = None):
        """
        Initialise le gestionnaire de cache
        
        Args:
            cache_size: Taille maximale du cache
            cache_ttl: TTL par défaut du cache
            circuit_config: Configuration du circuit breaker
        """
        self.tools_cache = LRUCache(cache_size, cache_ttl)
        self.response_cache = LRUCache(cache_size // 2, cache_ttl // 2)  # TTL plus court pour réponses
        
        circuit_config = circuit_config or CircuitBreakerConfig()
        self.circuit_breaker = CircuitBreaker(circuit_config)
        
        # Métriques globales
        self._start_time = time.time()
        self._metrics = {
            'cache_operations': 0,
            'circuit_breaker_calls': 0,
            'total_errors': 0
        }
        
        logger.info("CacheManager initialized")
    
    async def get_tools_cached(self, key: str) -> Optional[Any]:
        """Récupère les outils depuis le cache"""
        self._metrics['cache_operations'] += 1
        return await self.tools_cache.get(key)
    
    async def set_tools_cached(self, key: str, tools: Any, ttl: Optional[float] = None) -> None:
        """Met en cache la liste des outils"""
        await self.tools_cache.set(key, tools, ttl)
    
    async def get_response_cached(self, key: str) -> Optional[Any]:
        """Récupère une réponse depuis le cache"""
        self._metrics['cache_operations'] += 1
        return await self.response_cache.get(key)
    
    async def set_response_cached(self, key: str, response: Any, ttl: Optional[float] = None) -> None:
        """Met en cache une réponse"""
        await self.response_cache.set(key, response, ttl)
    
    async def protected_call(self, coro_func, *args, **kwargs) -> Any:
        """
        Appel protégé par le circuit breaker
        
        Args:
            coro_func: Fonction coroutine à protéger
            *args, **kwargs: Arguments de la fonction
            
        Returns:
            Résultat de la fonction
        """
        self._metrics['circuit_breaker_calls'] += 1
        try:
            return await self.circuit_breaker.call(coro_func, *args, **kwargs)
        except Exception as e:
            self._metrics['total_errors'] += 1
            raise
    
    async def cleanup(self) -> Dict[str, int]:
        """
        Nettoie les caches expirés
        
        Returns:
            Statistiques de nettoyage
        """
        tools_cleaned = await self.tools_cache.cleanup_expired()
        responses_cleaned = await self.response_cache.cleanup_expired()
        
        total_cleaned = tools_cleaned + responses_cleaned
        if total_cleaned > 0:
            logger.info(f"Cache cleanup: {total_cleaned} entries removed")
        
        return {
            'tools_cleaned': tools_cleaned,
            'responses_cleaned': responses_cleaned,
            'total_cleaned': total_cleaned
        }
    
    async def clear_all_caches(self) -> None:
        """Vide tous les caches"""
        await self.tools_cache.clear()
        await self.response_cache.clear()
        logger.info("All caches cleared")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques complètes"""
        uptime = time.time() - self._start_time
        
        tools_stats = self.tools_cache.get_stats()
        response_stats = self.response_cache.get_stats()
        circuit_stats = self.circuit_breaker.get_stats()
        
        return {
            'uptime_seconds': round(uptime, 2),
            'global_metrics': self._metrics,
            'tools_cache': tools_stats,
            'response_cache': response_stats,
            'circuit_breaker': {
                'state': circuit_stats.state.value,
                'failure_count': circuit_stats.failure_count,
                'success_count': circuit_stats.success_count,
                'total_requests': circuit_stats.total_requests,
                'successful_requests': circuit_stats.successful_requests,
                'success_rate_percent': round(
                    (circuit_stats.successful_requests / circuit_stats.total_requests * 100)
                    if circuit_stats.total_requests > 0 else 0, 2
                ),
                'last_failure': datetime.fromtimestamp(circuit_stats.last_failure_time).isoformat()
                    if circuit_stats.last_failure_time else None,
                'last_success': datetime.fromtimestamp(circuit_stats.last_success_time).isoformat()
                    if circuit_stats.last_success_time else None,
                'state_duration_seconds': round(time.time() - circuit_stats.state_change_time, 2),
                'is_available': self.circuit_breaker.is_available
            }
        }

# Instance globale du gestionnaire de cache
cache_manager = CacheManager()