# Gestion des entrées utilisateur
import asyncio
from config import active_channel_id, local_commands
from local_commands import handle_discord_command

async def get_user_input(bot):
    """Fonction qui lit en continu les entrées utilisateur et les traite"""
    
    while True:
        try:
            # Prompt qui indique le salon actif ou son absence
            prompt = f"[{bot.get_channel(active_channel_id).name if active_channel_id and bot.get_channel(active_channel_id) else 'Aucun salon'}] > "
            
            # Lecture de l'entrée utilisateur
            message = await asyncio.get_event_loop().run_in_executor(None, input, prompt)
            
            # Si l'entrée est vide, on continue
            if not message.strip():
                continue
            
            # Commande locale (préfixe /)
            if message.startswith('/'):
                parts = message[1:].split(' ')
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                if command in local_commands:
                    result = await local_commands[command]["function"](args) if args else await local_commands[command]["function"]()
                    if result is False:  # Pour gérer l'exit
                        break
                else:
                    print(f"Commande locale '{command}' non reconnue. Tapez /help pour l'aide.")
            
            # Commande Discord simplifiée (préfixe !!)
            elif message.startswith('!!'):
                parts = message[2:].split(' ')
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                await handle_discord_command(bot, command, args)
            
            # Texte sans préfixe - maintenant ignoré avec un message d'aide
            else:
                print("Entrée non reconnue. Utilisez /send pour envoyer un message ou /help pour voir les commandes disponibles.")
                
        except Exception as e:
            print(f"Erreur: {e}")

async def select_channel():
    """Permet à l'utilisateur de sélectionner un salon parmi ceux configurés"""
    
    print("\nSélection d'un salon Discord")
    print("Tapez /select <numéro ou ID> pour choisir un salon")
    print("Ou /channels pour voir la liste des salons disponibles")
    
    # On ne force plus la sélection, on laisse l'utilisateur utiliser les commandes
    return True