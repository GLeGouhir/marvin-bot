# Gestion des événements Discord
import asyncio  # Ajout de cet import manquant
import random
import re
from discord.errors import Forbidden
from config import active_channel_id
from russian_roulette import is_in_active_game, process_game_turn

async def setup_event_handlers(bot):
    """Configure les gestionnaires d'événements du bot"""
    
    @bot.event
    async def on_ready():
        """Événement déclenché lorsque le bot est connecté"""
        from config import CHANNEL_IDS
        from local_commands import register_local_commands
        from input_handler import get_user_input
        
        print(f'Bot connecté en tant que {bot.user}')
        print('----------------------------------------')
        print(f'ID du bot: {bot.user.id}')
        print(f'Salons configurés: {CHANNEL_IDS}')
        print('Bot prêt à transmettre les messages!')
        print('----------------------------------------')
        
        # Enregistrement des commandes locales
        register_local_commands(bot)
        
        # Démarre la boucle de saisie utilisateur comme une tâche asynchrone séparée
        asyncio.create_task(get_user_input(bot))
    
    @bot.event  # Correction de l'indentation de cette ligne
    async def on_message(message):
        """Événement déclenché lorsqu'un message est reçu"""
        # Ignore les messages du bot lui-même
        if message.author.bot:
            return
        
        author_id = str(message.author.id)
        
        # Vérifie si l'auteur est dans une partie active de roulette russe
        is_in_game, is_initiator, initiator_id = is_in_active_game(author_id)
        
        # Si l'auteur est dans une partie de roulette russe
        if is_in_game:
            print(f"[DEBUG] Traitement d'un message dans une partie: {initiator_id}")
            # Capture la valeur de retour pour savoir si la partie est terminée
            game_ended = await process_game_turn(message, is_initiator, initiator_id)
            if game_ended:
                return  # Si la partie est terminée, on ne traite pas comme une commande
        
        # Vérifie si le bot est mentionné dans le message
        if bot.user.mentioned_in(message):
            # Extrait le contenu du message sans la mention
            content = message.content.replace(f'<@{bot.user.id}>', '').strip()
            
            # Réponse préprogrammée (simulation d'un service LLM)
            response = 'je suis viv###ant rrrr bzzzzz rrrrr bzzzz aaaaaarrrg3,1415926^^ ++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>. !!,'
            
            # Envoie la réponse dans le salon
            await message.channel.send(response)
        
        # Continue le traitement normal des autres messages
        await bot.process_commands(message)