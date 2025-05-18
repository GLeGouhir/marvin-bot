# Configuration et variables d'environnement
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration
TOKEN = os.getenv('DISCORD_TOKEN')
# Liste des IDs de salons où le bot peut envoyer des messages
CHANNEL_IDS = os.getenv('CHANNEL_IDS', '').split(',')
CHANNEL_IDS = [int(id.strip()) for id in CHANNEL_IDS if id.strip()]

# Variable pour stocker le salon actif (initialisée à None)
active_channel_id = None

# Dictionnaire des commandes locales
local_commands = {}

# Structure pour stocker les parties de roulette russe actives
# Cette variable est partagée entre les différents modules
active_rolls = {}