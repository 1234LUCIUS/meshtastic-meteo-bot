# Documentation du Bot météo MT/MC

Le projet est organisé en trois couches :

- `bot/` contient la logique du bot et les adaptateurs radio ;
- `services/` contient les services météo, vigilance, actualités et cache ;
- `docs/` décrit séparément les backends radio et leurs options réellement disponibles.

Les deux firmwares utilisent le même contrôleur et les mêmes commandes. Seul l’adaptateur de transport change.

## Commandes communes

Ces commandes sont disponibles avec Meshtastic et MeshCore :

| Commande | Fonction |
|---|---|
| `!meteo` | Météo à la position par défaut, ou à la position GPS du paquet si elle est disponible |
| `!meteo <ville>` | Météo d’une ville |
| `!alertes [département]` | Vigilance Météo-France |
| `!crues` | Alertes Vigicrues |
| `!feux [département]` | Météo des Forêts |
| `!suivi_feux` | Feux actifs autour de la position configurée |
| `!normandie` | Informations officielles Normandie |
| `!actu <ville>` | Actualités récentes d’une ville |
| `!officiel` | Résumé des sources officielles |
| `!urgence <thème>` | Consignes de sécurité hors ligne |
| `!canal <0-7>` | Change le canal de diffusion périodique |
| `!ping` | Vérifie que le bot répond |
| `!aide` | Affiche cette liste côté radio |

La commande `!ia` n’est pas activée dans le parseur actuel et n’est donc pas présentée comme disponible.

## Détection automatique

`MESH_NETWORK=auto` est le mode recommandé. Le bot essaie d’abord le handshake MeshCore, puis Meshtastic si MeshCore ne répond pas. Le firmware retenu est écrit dans les logs et dans le message de démarrage.

Pour éviter une détection ambiguë sur un port série, renseignez le même port dans les deux variables correspondantes, ou forcez le backend avec `--network meshtastic` ou `--network meshcore`.

## Choix manuel

```bash
python main.py --network auto
python main.py --network meshtastic
python main.py --network meshcore
python main.py --simulate --network meshcore
```

La simulation ne nécessite aucun matériel. Les commandes de services peuvent également être testées avec les options `--test-*` de `main.py`.

## Guides par firmware

- [Utiliser Meshtastic](meshtastic.md)
- [Utiliser MeshCore](meshcore.md)
