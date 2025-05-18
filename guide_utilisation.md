# Guide d'utilisation du Bot Discord modularisé

## Installation

1. Clonez le dépôt ou créez les fichiers dans un dossier dédié
2. Installez les dépendances:
   ```
   pip install discord.py python-dotenv
   ```
3. Copiez le fichier `.env.example` en `.env` et remplissez-le avec vos informations:
   ```
   cp .env.example .env
   ```
4. Modifiez le fichier `.env` avec votre token Discord et les IDs des salons

## Structure du projet

Le projet a été divisé en plusieurs fichiers pour faciliter la maintenance et l'ajout de nouvelles fonctionnalités:

- `main.py` - Point d'entrée principal, initialise et lance le bot
- `config.py` - Configuration et variables d'environnement
- `local_commands.py` - Commandes locales (préfixe /)
- `discord_commands.py` - Commandes Discord (préfixe !)
- `russian_roulette.py` - Logique de la fonctionnalité de roulette russe
- `event_handlers.py` - Gestionnaires d'événements Discord
- `input_handler.py` - Gestion des entrées utilisateur
- `.env` - Variables d'environnement (token, IDs des salons)

## Lancement du bot

```
python main.py
```

## Ajout de nouvelles commandes

### Ajouter une commande locale (préfixe /)

Pour ajouter une nouvelle commande locale, modifiez `local_commands.py` et ajoutez une nouvelle fonction dans `register_local_commands()`:

```python
async def cmd_ma_nouvelle_commande(args):
    """Description de ma nouvelle commande"""
    # Logique de votre commande
    print("Ma commande a été exécutée!")
    return True

# Puis enregistrez-la
register_local_command("ma_nouvelle_commande", cmd_ma_nouvelle_commande, "Description de ma nouvelle commande")
```

### Ajouter une commande Discord (préfixe !)

Pour ajouter une nouvelle commande Discord, modifiez `discord_commands.py` dans la fonction `setup_discord_commands()`:

```python
@bot.command()
async def ma_nouvelle_commande(ctx, *, message):
    """Description de ma nouvelle commande Discord"""
    # Logique de votre commande
    await ctx.send(f"Commande exécutée avec: {message}")
```

### Ajouter une fonctionnalité complexe

Si vous souhaitez ajouter une fonctionnalité complexe comme la roulette russe:

1. Créez un nouveau fichier pour votre fonctionnalité (ex: `ma_fonctionnalite.py`)
2. Définissez les constantes, variables et fonctions nécessaires
3. Importez et utilisez cette fonctionnalité depuis d'autres modules

## Commandes disponibles

### Commandes locales (préfixe /)
- `/help` - Affiche l'aide des commandes
- `/channels` - Affiche la liste des salons disponibles
- `/select` - Change le salon actif
- `/status` - Affiche l'état du bot
- `/send` - Envoie un message dans le salon actif
- `/exit` - Arrête le bot

### Commandes Discord simplifiées (préfixe !!)
- `!!ping` - Fait répondre le bot 'Bite!'
- `!!send <channel_id> <message>` - Envoie un message dans un salon spécifique

### Commandes Discord du bot (préfixe !)
- `!ping` - Test de connexion
- `!echo <message>` - Répète le message
- `!channels` - Liste les salons configurés
- `!pseudo @utilisateur <nouveau_pseudo>` - Change le pseudo d'un utilisateur
- `!russian_roll @utilisateur "sujet"` - Lance une partie de roulette russe
- `!cancel_roll` - Annule une partie de roulette russe en cours
