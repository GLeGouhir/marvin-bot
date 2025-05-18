import discord
from discord.ext import commands, tasks
import asyncio
import os
import sys
import importlib
import logging
import time

# Import des modules personnalisés
from config import TOKEN, CHANNEL_IDS
from discord_commands import setup_discord_commands
from event_handlers import setup_event_handlers

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("discord_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("bot")

# Création du bot
def create_bot():
    """Crée et configure l'instance du bot Discord"""
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)
    return bot

# Nouvelle fonction pour gérer la reconnexion
async def run_bot_with_reconnect():
    """Exécute le bot avec gestion de reconnexion automatique"""
    bot = create_bot()
    
    # Configuration des gestionnaires d'événements
    await setup_event_handlers(bot)
    
    # Configuration des commandes Discord
    await setup_discord_commands(bot)
    
    # Ajouter l'événement de déconnexion
    @bot.event
    async def on_disconnect():
        logger.warning("Bot déconnecté du serveur Discord")
    
    # Ajouter une tâche périodique pour surveiller la connexion
    @tasks.loop(minutes=5)
    async def check_connection():
        if not bot.is_ready():
            logger.warning("Bot non connecté, tentative de reconnexion...")
            try:
                await bot.close()  # Fermer proprement la connexion existante
                await asyncio.sleep(5)  # Attendre un peu avant de retenter
                await bot.start(TOKEN)
            except Exception as e:
                logger.error(f"Échec de reconnexion: {e}")
    
    # Démarrer la tâche de surveillance après le démarrage du bot
    @bot.event
    async def on_ready():
        # Exécuter l'événement on_ready original
        from config import CHANNEL_IDS
        from local_commands import register_local_commands
        from input_handler import get_user_input
        
        logger.info(f'Bot connecté en tant que {bot.user}')
        logger.info('----------------------------------------')
        logger.info(f'ID du bot: {bot.user.id}')
        logger.info(f'Salons configurés: {CHANNEL_IDS}')
        logger.info('Bot prêt à transmettre les messages!')
        logger.info('----------------------------------------')
        
        # Enregistrement des commandes locales
        register_local_commands(bot)
        
        # Démarre la boucle de saisie utilisateur comme une tâche asynchrone séparée
        asyncio.create_task(get_user_input(bot))
        
        # Démarrer la tâche de surveillance de connexion si elle n'est pas déjà en cours
        if not check_connection.is_running():
            check_connection.start()
    
    # Boucle de reconnexion
    retry_count = 0
    max_retries = 10
    retry_delay = 30  # secondes
    
    while retry_count < max_retries:
        try:
            logger.info(f"Tentative de connexion ({retry_count + 1}/{max_retries})...")
            await bot.start(TOKEN)
        except discord.errors.LoginFailure:
            # Erreur d'authentification - ne pas réessayer
            logger.critical("Échec d'authentification - token invalide")
            return 1
        except Exception as e:
            retry_count += 1
            wait_time = retry_delay * retry_count
            logger.error(f"Erreur de connexion: {e}")
            logger.info(f"Nouvelle tentative dans {wait_time} secondes...")
            await asyncio.sleep(wait_time)
        else:
            # Si on arrive ici, c'est que le bot s'est déconnecté normalement
            retry_count = 0
            logger.info("Bot déconnecté normalement")
            await asyncio.sleep(5)  # Petit délai avant de tenter de redémarrer
    
    logger.critical(f"Nombre maximal de tentatives atteint ({max_retries}). Arrêt du bot.")
    return 1

async def main():
    """Fonction principale qui initialise et démarre le bot"""
    return await run_bot_with_reconnect()
    
# Point d'entrée
if __name__ == "__main__":
    # Utilisation de asyncio.run pour exécuter la fonction principale
    exit_code = asyncio.run(main())
    sys.exit(exit_code)