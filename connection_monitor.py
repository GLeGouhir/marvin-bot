# connection_monitor.py
# Surveillance et gestion de la connexion du bot Discord

import asyncio
import logging
import time
import socket
from discord.ext import tasks

logger = logging.getLogger("bot")

class ConnectionMonitor:
    """Classe qui surveille et gère la connexion du bot Discord"""
    
    def __init__(self, bot, token):
        self.bot = bot
        self.token = token
        self.last_connected = time.time()
        self.disconnected_since = None
        self.max_disconnect_time = 300  # 5 minutes
        self.check_interval = 60  # 1 minute
        self.monitor_task = None
        self.internet_check_hosts = [
            ("8.8.8.8", 53),  # Google DNS
            ("1.1.1.1", 53),  # Cloudflare DNS
            ("208.67.222.222", 53)  # OpenDNS
        ]
    
    def start(self):
        """Démarre la surveillance de connexion"""
        self.monitor_connection.start()
        logger.info("Surveillance de connexion démarrée")
    
    def stop(self):
        """Arrête la surveillance de connexion"""
        if self.monitor_connection.is_running():
            self.monitor_connection.cancel()
            logger.info("Surveillance de connexion arrêtée")
    
    def has_internet(self):
        """Vérifie si l'ordinateur a une connexion Internet"""
        for host, port in self.internet_check_hosts:
            try:
                socket.create_connection((host, port), timeout=3)
                return True
            except OSError:
                pass
        return False
    
    @tasks.loop(seconds=60)
    async def monitor_connection(self):
        """Vérifie périodiquement l'état de la connexion et tente de reconnecter si nécessaire"""
        # Si le bot est connecté, mettre à jour le timestamp
        if self.bot.is_ready():
            if self.disconnected_since is not None:
                logger.info(f"Bot reconnecté après {time.time() - self.disconnected_since:.2f} secondes")
                self.disconnected_since = None
            self.last_connected = time.time()
            return
            
        # Si le bot est déconnecté
        current_time = time.time()
        if self.disconnected_since is None:
            self.disconnected_since = current_time
            logger.warning("Bot déconnecté, surveillance active")
        
        disconnect_duration = current_time - self.disconnected_since
        
        # Vérifier si la déconnexion dure depuis trop longtemps
        if disconnect_duration > self.max_disconnect_time:
            # Vérifier si Internet est disponible
            if not self.has_internet():
                logger.warning("Pas de connexion Internet détectée, attente...")
                return
                
            logger.warning(f"Déconnecté depuis {disconnect_duration:.0f}s, tentative de reconnexion forcée")
            
            try:
                # Fermer proprement la connexion existante
                await self.bot.close()
                await asyncio.sleep(5)
                
                # Tenter de redémarrer le bot
                logger.info("Tentative de reconnexion forcée...")
                await self.bot.start(self.token)
            except Exception as e:
                logger.error(f"Échec de la tentative de reconnexion forcée: {e}")
                
    @monitor_connection.before_loop
    async def before_monitor(self):
        """Attend que le bot soit prêt avant de démarrer la surveillance"""
        await self.bot.wait_until_ready()
        logger.info("Bot prêt, démarrage de la surveillance de connexion")
