# Bot Discord Simple - Transmet vos messages depuis le PC vers plusieurs salons Discord
import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
import os
import sys
import importlib

# Chargement des variables d'environnement
load_dotenv()

# Configuration
TOKEN = os.getenv('DISCORD_TOKEN')
# Liste des IDs de salons où le bot peut envoyer des messages
CHANNEL_IDS = os.getenv('CHANNEL_IDS', '').split(',')
CHANNEL_IDS = [int(id.strip()) for id in CHANNEL_IDS if id.strip()]

# Création du bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Variable pour stocker le salon actif
active_channel_id = None

# Dictionnaire des commandes locales
local_commands = {}

def register_local_command(name, func, description=""):
    """Enregistre une commande locale"""
    local_commands[name] = {
        "function": func,
        "description": description
    }

@bot.event
async def on_ready():
    print(f'Bot connecté en tant que {bot.user}')
    print('----------------------------------------')
    print(f'ID du bot: {bot.user.id}')
    print(f'Salons configurés: {CHANNEL_IDS}')
    print('Bot prêt à transmettre les messages!')
    print('----------------------------------------')
    
    # Enregistrement des commandes locales
    register_local_commands()
    
    # Démarre la boucle de saisie utilisateur
    await get_user_input()

def register_local_commands():
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
        channel = bot.get_channel(active_channel_id) if active_channel_id else None
        print(f"\nÉtat du bot:")
        print(f"- Connecté en tant que: {bot.user}")
        print(f"- Salon actif: {channel.name if channel else 'Aucun'}")
        print(f"- Latence: {round(bot.latency * 1000)}ms")
        print(f"- Serveurs connectés: {len(bot.guilds)}")
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

async def handle_discord_command(command, args):
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

async def get_user_input():
    """Fonction qui lit en continu les entrées utilisateur et les traite"""
    global active_channel_id
    
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
                await handle_discord_command(command, args)
            
            # Texte sans préfixe - maintenant ignoré avec un message d'aide
            else:
                print("Entrée non reconnue. Utilisez /send pour envoyer un message ou /help pour voir les commandes disponibles.")
                
        except Exception as e:
            print(f"Erreur: {e}")

async def select_channel():
    """Permet à l'utilisateur de sélectionner un salon parmi ceux configurés"""
    global active_channel_id
    
    print("\nSélection d'un salon Discord")
    print("Tapez /select <numéro ou ID> pour choisir un salon")
    print("Ou /channels pour voir la liste des salons disponibles")
    
    # On ne force plus la sélection, on laisse l'utilisateur utiliser les commandes
    return True

# Commandes Discord normales (restent inchangées)
@bot.command()
async def ping(ctx):
    """Commande de test pour vérifier que le bot fonctionne"""
    await ctx.send('Bite!')

@bot.command()
async def echo(ctx, *, message):
    '''Commande de test pour que le bot renvoie exactement le texte reçu'''
    await ctx.send(message)

@bot.command()
async def channels(ctx):
    """Affiche la liste des salons configurés"""
    if not CHANNEL_IDS:
        await ctx.send("Aucun salon n'est configuré.")
        return
    
    response = "Salons configurés:\n"
    for channel_id in CHANNEL_IDS:
        channel = bot.get_channel(channel_id)
        if channel:
            response += f"- {channel.name} (ID: {channel_id})\n"
        else:
            response += f"- ID: {channel_id} (salon non trouvé)\n"
    
    await ctx.send(response)

@bot.command()
async def pseudo(ctx, member: discord.Member, *, new_nickname):
    """Change le pseudo d'un utilisateur. Usage: !nickname @user NouveauPseudo"""
    try:
        # Vérifie si l'auteur possède le rôle "Primate Angoissé"
        primate_role = discord.utils.get(ctx.guild.roles, name="Primate Angoissé")
        if primate_role not in ctx.author.roles:
            await ctx.send("Non.")
            return
        
        # Vérifie si l'utilisateur essaie de renommer le bot lui-même
        if member.id == bot.user.id:
            await ctx.send(f"Mais quel malin. Dis moi, {ctx.author.display_name}, il te manquerait pas un quart d'heure de cuisson toi?")
            return
        
        # Vérifie si le bot a la permission de gérer les pseudos
        if not ctx.guild.me.guild_permissions.manage_nicknames:
            await ctx.send("Je n'ai pas la permission de changer les pseudos !")
            return
        
        # Vérifie si le membre ciblé n'est pas le propriétaire
        if member.id == ctx.guild.owner_id:
            await ctx.send("Je ne toucherai pas à Dieu !")
            return
        
        # Vérifie si la hiérarchie des rôles permet le changement
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send("Non.")
            return
        
        # Change le pseudo
        old_nickname = member.display_name
        await member.edit(nick=new_nickname)
        # await ctx.send(f"Pseudo changé de '{old_nickname}' à '{new_nickname}' pour {member.mention}")
        
    except discord.Forbidden:
        await ctx.send("Pas possible.")
    except discord.HTTPException as e:
        await ctx.send(f"Une erreur s'est produite: {str(e)}")

# Ajout d'un écouteur pour les messages dans les salons configurés
@bot.event
async def on_message(message):
    # Ignore les messages du bot lui-même
    if message.author == bot.user:
        return
    
    # Vérifie si le bot est mentionné dans le message
    if bot.user.mentioned_in(message):
        # Extrait le contenu du message sans la mention
        content = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        # Appelle le service LLM pour générer une réponse
        #response = await llm_service.generate_sarcastic_response(content)
        response = 'je suis viv###ant rrrr bzzzzz rrrrr bzzzz aaaaaarrrg3,1415926^^ ++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>. !!,'
        # Envoie la réponse dans le salon
        await message.channel.send(response)
    
    # Continue le traitement normal des autres messages
    await bot.process_commands(message)
# Lancement du bot
if __name__ == "__main__":
    bot.run(TOKEN)