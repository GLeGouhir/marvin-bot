# Messages et logique pour la roulette russe
import random
from discord.errors import Forbidden
from config import active_rolls  # Import crucial pour le partage des données entre modules

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

# Fonction pour vérifier l'existence d'une partie active
def is_in_active_game(member_id):
    """Vérifie si un membre est dans une partie active (initiateur ou cible)"""
    # Debug: afficher les parties actives
    print(f"[DEBUG] Vérification de l'existence d'une partie pour {member_id}. Parties actives: {active_rolls}")
    
    # Vérifie si le membre est initiateur
    if member_id in active_rolls:
        return True, True, member_id  # is_in_game, is_initiator, initiator_id
    
    # Vérifie si le membre est cible
    for initiator_id, game in active_rolls.items():
        if game["target_id"] == member_id:
            return True, False, initiator_id  # is_in_game, is_initiator, initiator_id
    
    return False, False, None  # Pas dans une partie active

# Fonction pour gérer un tour de jeu
async def process_game_turn(message, is_initiator, initiator_id):
    """Traite un tour de jeu de la roulette russe"""
    print(f"[DEBUG] Traitement tour de jeu pour {initiator_id}, active_rolls: {active_rolls}")
    
    if initiator_id not in active_rolls:
        print(f"[ERROR] Partie non trouvée pour l'initiateur: {initiator_id}")
        return False
    
    author_id = str(message.author.id)
    game_data = active_rolls[initiator_id]
    
    # Récupère les IDs des joueurs
    game_initiator_id = initiator_id
    game_target_id = game_data["target_id"]
    
    # Convertit en objets discord.Member
    initiator = message.guild.get_member(int(game_initiator_id))
    target = message.guild.get_member(int(game_target_id))
    
    # Vérifie si le message est dans le bon salon
    if str(message.channel.id) != game_data["channel_id"]:
        return False
    
    # Vérifie si le message mentionne l'autre joueur
    other_player_id = game_target_id if is_initiator else game_initiator_id
    other_player = message.guild.get_member(int(other_player_id))
    
    mentions_other_player = any(mentioned.id == int(other_player_id) for mentioned in message.mentions)
    
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
        
        return False
    
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
        del active_rolls[initiator_id]
        print(f"[DEBUG] Partie terminée: {initiator.display_name} vs {target.display_name}, {message.author.display_name} a perdu")
        return True  # Partie terminée
    else:
        # Clic! Message de survie
        click_message = random.choice(ROLL_CLICK_MESSAGES).replace("{user}", message.author.mention)
        await message.channel.send(click_message)
        
        # Met à jour la position dans le dictionnaire
        active_rolls[initiator_id]["current_position"] = current_position
        print(f"[DEBUG] Tour {current_position}/6, balle en position {bullet_position}")
        return False  # Partie continue