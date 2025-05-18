# Gestion des commandes locales
import asyncio
from config import active_channel_id, local_commands, CHANNEL_IDS

def register_local_command(name, func, description=""):
    """Enregistre une commande locale"""
    local_commands[name] = {
        "function": func,
        "description": description
    }

def register_local_commands(bot):
    """Enregistre toutes les commandes locales disponibles"""
    
    async def cmd_channels():
        """Affiche la liste des salons disponibles"""
        print("\nSalons disponibles:")
        for i, channel_id in enumerate(CHANNEL_IDS):
            channel = bot.get_channel(channel_id)
            if channel:
                print(f"{i}. {channel.name} (ID: {channel_id})")
            else:
                print(f"{i}. ID: {channel_id} (salon non trouvé)")
        return True
    
    async def cmd_select(args):
        """Change le salon actif"""
        global active_channel_id
        if not args:
            print("Usage: /select <id ou index>")
            return False
        
        try:
            # Essaie de convertir l'argument en index
            index = int(args[0])
            if 0 <= index < len(CHANNEL_IDS):
                active_channel_id = CHANNEL_IDS[index]
                channel = bot.get_channel(active_channel_id)
                print(f"Salon actif: {channel.name if channel else active_channel_id}")
                return True
        except ValueError:
            # Essaie de convertir directement en ID
            try:
                channel_id = int(args[0])
                if channel_id in CHANNEL_IDS:
                    active_channel_id = channel_id
                    channel = bot.get_channel(active_channel_id)
                    print(f"Salon actif: {channel.name if channel else active_channel_id}")
                    return True
            except ValueError:
                pass
        
        print("ID ou index invalide")
        return False
    
    async def cmd_status():
        """Affiche l'état actuel du bot"""
        from russian_roulette import active_rolls
        
        channel = bot.get_channel(active_channel_id) if active_channel_id else None
        print(f"\nÉtat du bot:")
        print(f"- Connecté en tant que: {bot.user}")
        print(f"- Salon actif: {channel.name if channel else 'Aucun'}")
        print(f"- Latence: {round(bot.latency * 1000)}ms")
        print(f"- Serveurs connectés: {len(bot.guilds)}")
        print(f"- Parties de roulette active: {len(active_rolls)}")
        return True
    
    async def cmd_help():
        """Affiche l'aide des commandes"""
        print("\nCommandes disponibles:")
        print("\nCommandes locales (préfixe /):")
        for name, data in local_commands.items():
            print(f"  /{name} - {data['description']}")
        
        print("\nCommandes Discord simplifiées (préfixe !!):")
        print("  !!ping - Fait répondre le bot 'Bite!'")
        print("  !!send <channel_id> <message> - Envoie un message dans un salon spécifique")
        
        print("\nCommandes Discord du bot:")
        print("  !ping - Test de connexion")
        print("  !echo <message> - Répète le message")
        print("  !channels - Liste les salons configurés")
        print("  !pseudo @utilisateur <nouveau_pseudo> - Change le pseudo d'un utilisateur")
        print("  !russian_roll @utilisateur \"sujet\" - Lance une partie de roulette russe")
        print("  !cancel_roll - Annule une partie de roulette russe en cours")
        
        print("\nNote: Tout texte sans préfixe est ignoré. Utilisez /send pour envoyer des messages.")
        return True
    
    async def cmd_exit():
        """Arrête proprement le bot"""
        print("Arrêt du bot...")
        await bot.close()
        return False
    
    async def cmd_send(args):
        """Envoie un message dans le salon actif"""
        if not args:
            print("Usage: /send <message>")
            return True
        
        if not active_channel_id:
            print("Aucun salon actif. Utilisez /select d'abord.")
            return True
        
        channel = bot.get_channel(active_channel_id)
        if channel:
            message = " ".join(args)
            await channel.send(message)
            print(f"→ {channel.name}: {message}")
        else:
            print(f"Impossible de trouver le salon {active_channel_id}")
        return True
    
    register_local_command("channels", cmd_channels, "Affiche la liste des salons")
    register_local_command("select", cmd_select, "Change le salon actif")
    register_local_command("status", cmd_status, "Affiche l'état du bot")
    register_local_command("help", cmd_help, "Affiche cette aide")
    register_local_command("exit", cmd_exit, "Arrête le bot")
    register_local_command("send", cmd_send, "Envoie un message dans le salon actif")

async def handle_discord_command(bot, command, args):
    """Gère les commandes Discord simplifiées"""
    if command == "ping":
        # Envoie "Bite!" dans le salon actif
        channel = bot.get_channel(active_channel_id)
        if channel:
            await channel.send("Bite!")
            print(f"Commande ping exécutée dans {channel.name}")
        else:
            print("Aucun salon actif. Utilisez /select d'abord.")
    
    elif command == "send":
        # Format: !!send <channel_id> <message>
        if len(args) < 2:
            print("Usage: !!send <channel_id> <message>")
            return
        
        try:
            channel_id = int(args[0])
            message = " ".join(args[1:])
            channel = bot.get_channel(channel_id)
            
            if channel:
                await channel.send(message)
                print(f"Message envoyé dans {channel.name}")
            else:
                print(f"Salon {channel_id} non trouvé")
        except ValueError:
            print("ID de salon invalide")
    
    else:
        print(f"Commande Discord '{command}' non reconnue")
