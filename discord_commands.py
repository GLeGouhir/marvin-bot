# Gestion des commandes Discord
import discord
import random
from config import active_rolls

async def setup_discord_commands(bot):
    """Configure les commandes du bot Discord"""
    
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
        from config import CHANNEL_IDS
        
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
        from russian_roulette import ROLL_START_MESSAGES
        
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
