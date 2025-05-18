# Bot Discord Simple - Transmet vos messages depuis le PC vers plusieurs salons Discord
import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
import os
import sys
import importlib
import random
from discord.errors import Forbidden
import re

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

# Structure pour stocker les parties de roulette russe actives
active_rolls = {}

# Messages humoristiques pour la roulette russe
ROLL_START_MESSAGES = [
    "🎩 \"Le barillet est chargé, le sujet est posé : « {subject} ». {initiator} provoque {target} en duel... Que le sort décide du vaincu !\"",
    "🔫 \"Un seul cran dans le barillet, deux cerveaux en surchauffe. {initiator} vs {target} sur le thème « {subject} ». Clic ou boum ?\"",
    "😈 \"{initiator} vient de tendre le revolver à {target}… sur « {subject} ». Les balles sont verbales. Ou pas.\"",
    "🐒 \"Deux primates, une balle, six chambres, et un sujet : « {subject} ». Bonne chance, {initiator} et {target}. Enfin… surtout à l'un de vous.\"",
    "🤠 \"{initiator} fixe {target} et murmure : « Parlons de « {subject} »… si tu l'oses. » Le barillet tourne.\"",
    "🎭 \"La scène est prête, les acteurs aussi. Sujet : « {subject} ». Qui rira le dernier ?\"",
    "🕳️ \"Un trou, un clic, un silence gênant. {initiator} et {target} entrent dans le cercle. Roulette russe sur « {subject} » enclenchée.\""
]

ROLL_CLICK_MESSAGES = [
    "Clic... ça passe pour cette fois.",
    "Le barillet tourne, mais la chambre est vide.",
    "Le destin t'épargne... temporairement.",
    "💨 L'air s'échappe du canon. Une chance de plus.",
    "Clic. La sueur perle sur ton front.",
    "La mort te fait un clin d'œil... mais pas aujourd'hui.",
    "Le métal froid du canon ne fait même plus frémir {user}."
]

ROLL_BANG_MESSAGES = [
    "💥 BANG! Et voilà, {loser} vient de s'exploser la cervelle sur « {subject} ».",
    "🔫 BOOM! {loser} a perdu. La roulette russe ne pardonne pas.",
    "💀 La partie est terminée. {loser} rejoint les perdants de l'histoire.",
    "🤯 Le coup est parti! {loser} n'est plus des nôtres... intellectuellement parlant.",
    "⚰️ On applaudit {loser} qui vient de perdre avec panache!"
]

ROLL_ESCAPE_MESSAGES = [
    "🧠 On a dit un duel. Pas un monologue.",
    "🚪 Tu ne peux pas sortir de la pièce tant que le coup n'est pas parti.",
    "🏃 La roulette ne tolère pas les lâches.",
    "🔇 Tu peux parler, mais personne n'écoute tant que tu ne vises pas ton adversaire.",
    "💬 Pas d'échappatoire. Mentionne ton adversaire ou tais-toi.",
    "⛓️ Chaque mot t'éloigne du salut… sauf si tu vises l'autre.",
    "🤫 Pas de diversion, pas d'échappatoire. C'est un duel, pas un débat."
]

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

# Commandes Discord normales
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

@bot.command()
async def russian_roll(ctx, target: discord.Member = None, *, subject: str = None):
    """
    Démarre une partie de roulette russe avec un autre membre.
    Usage: !russian_roll @utilisateur "sujet"
    """
    # Vérification des arguments
    if not target:
        await ctx.send("❌ Veuillez mentionner un utilisateur pour lancer une partie de roulette russe.")
        return
    
    if target.id == ctx.author.id:
        await ctx.send("❌ Vous ne pouvez pas jouer contre vous-même. Trouvez une autre victime.")
        return
    
    if target.bot:
        await ctx.send("❌ Les bots n'ont pas de cerveau à faire exploser. Choisissez un humain.")
        return
    
    if not subject:
        await ctx.send("❌ Veuillez spécifier un sujet pour la roulette russe. Usage: !russian_roll @utilisateur \"sujet\"")
        return
    
    # Vérification si l'initiateur a déjà une partie en cours
    initiator_id = str(ctx.author.id)
    if initiator_id in active_rolls:
        await ctx.send(f"❌ Vous avez déjà une partie en cours avec {bot.get_user(int(active_rolls[initiator_id]['target_id'])).mention}. Terminez-la d'abord.")
        return
    
    # Vérification si la cible a déjà une partie en cours comme initiateur
    target_id = str(target.id)
    if target_id in active_rolls:
        await ctx.send(f"❌ {target.mention} a déjà initié une partie. Demandez-lui de terminer sa partie d'abord.")
        return
    
    # Création de la nouvelle partie
    bullet_position = random.randint(1, 6)  # Position de la balle (1-6)
    
    active_rolls[initiator_id] = {
        "target_id": target_id,
        "channel_id": str(ctx.channel.id),
        "subject": subject,
        "bullet_position": bullet_position,
        "current_position": 0,  # Le message d'initialisation est la position 0
        "status": "active"
    }
    
    # Message de départ
    start_message = random.choice(ROLL_START_MESSAGES).format(
        initiator=ctx.author.mention,
        target=target.mention,
        subject=subject
    )
    
    await ctx.send(start_message)
    
    # Debug (à retirer en production)
    print(f"[DEBUG] Nouvelle partie: {initiator_id} vs {target_id}, balle en position {bullet_position}")

@bot.command()
async def cancel_roll(ctx):
    """Annule une partie de roulette russe en cours"""
    author_id = str(ctx.author.id)
    
    # Vérifie si l'auteur est initiateur d'une partie
    if author_id in active_rolls:
        # Récupère les données de la partie
        game_data = active_rolls[author_id]
        target = ctx.guild.get_member(int(game_data["target_id"]))
        
        # Annonce l'annulation
        await ctx.send(f"🚫 {ctx.author.mention} a mis fin à sa partie de roulette russe avec {target.mention}. Lâche!")
        
        # Supprime la partie
        del active_rolls[author_id]
    else:
        # Vérifie si l'auteur est cible d'une partie
        for initiator_id, game in active_rolls.items():
            if game["target_id"] == author_id:
                initiator = ctx.guild.get_member(int(initiator_id))
                
                # Annonce l'annulation
                await ctx.send(f"🚫 {ctx.author.mention} a refusé de continuer la partie de roulette russe avec {initiator.mention}. Lâche!")
                
                # Supprime la partie
                del active_rolls[initiator_id]
                return
        
        # Si l'auteur n'est pas dans une partie
        await ctx.send("❌ Vous n'avez pas de partie de roulette russe en cours.")

@bot.event
async def on_message(message):
    # Ignore les messages du bot lui-même
    if message.author.bot:
        return
    
    author_id = str(message.author.id)
    
    # Vérifie si l'auteur est dans une partie active de roulette russe (comme initiateur ou cible)
    is_initiator = author_id in active_rolls
    is_target = False
    
    initiator_id = None
    if not is_initiator:
        # Vérifie si l'auteur est une cible
        for init_id, game in active_rolls.items():
            if game["target_id"] == author_id:
                is_target = True
                initiator_id = init_id
                break
    
    # Si l'auteur est dans une partie de roulette russe
    if is_initiator or is_target:
        game_data = active_rolls[author_id] if is_initiator else active_rolls[initiator_id]
        
        # Récupère les IDs des joueurs
        game_initiator_id = author_id if is_initiator else initiator_id
        game_target_id = game_data["target_id"] if is_initiator else author_id
        
        # Convertit en objets discord.Member
        initiator = message.guild.get_member(int(game_initiator_id))
        target = message.guild.get_member(int(game_target_id))
        
        # Vérifie si le message est dans le bon salon
        if str(message.channel.id) != game_data["channel_id"]:
            return
        
        # Vérifie si le message mentionne l'autre joueur
        other_player_id = game_target_id if is_initiator else game_initiator_id
        other_player = message.guild.get_member(int(other_player_id))
        
        mentions_other_player = False
        for mentioned in message.mentions:
            if mentioned.id == int(other_player_id):
                mentions_other_player = True
                break
        
        if not mentions_other_player:
            # Supprime le message
            try:
                await message.delete()
                
                # Envoie un message privé de tentative d'évasion
                escape_message = random.choice(ROLL_ESCAPE_MESSAGES)
                try:
                    await message.author.send(escape_message)
                except Forbidden:
                    # Si les DMs sont désactivés, on envoie un message éphémère dans le salon
                    await message.channel.send(
                        f"{message.author.mention}: {escape_message}", 
                        delete_after=5
                    )
            except Exception as e:
                print(f"[ERROR] Impossible de supprimer le message: {e}")
            
            return
        
        # Message valide avec mention, on fait avancer le jeu
        game_data["current_position"] += 1
        current_position = game_data["current_position"]
        bullet_position = game_data["bullet_position"]
        
        # Vérifie si la balle est tirée
        if current_position == bullet_position:
            # BANG! Le joueur actuel perd
            bang_message = random.choice(ROLL_BANG_MESSAGES).format(
                loser=message.author.mention,
                subject=game_data["subject"]
            )
            
            await message.channel.send(bang_message)
            
            # Fin de partie
            if is_initiator:
                del active_rolls[author_id]
            else:
                del active_rolls[initiator_id]
                
            print(f"[DEBUG] Partie terminée: {initiator.display_name} vs {target.display_name}, {message.author.display_name} a perdu")
        else:
            # Clic! Message de survie
            click_message = random.choice(ROLL_CLICK_MESSAGES).replace("{user}", message.author.mention)
            await message.channel.send(click_message)
            
            # Met à jour la position dans le dictionnaire
            if is_initiator:
                active_rolls[author_id]["current_position"] = current_position
            else:
                active_rolls[initiator_id]["current_position"] = current_position
                
            print(f"[DEBUG] Tour {current_position}/6, balle en position {bullet_position}")
    
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
