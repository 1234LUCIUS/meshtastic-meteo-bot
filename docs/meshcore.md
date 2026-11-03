# Backend MeshCore

Le backend MeshCore est implémenté dans `bot/meshcore_client.py`. Il utilise la bibliothèque Python officielle `meshcore` et exécute sa boucle asyncio dans un thread dédié afin de conserver le contrôleur synchrone du bot.

## Transports disponibles

| Transport | Variables | Disponible |
|---|---|---:|
| Série / USB | `MESHCORE_CONNECTION_TYPE=serial`, `MESHCORE_SERIAL_PORT`, `MESHCORE_BAUDRATE` | Oui |
| TCP | `MESHCORE_CONNECTION_TYPE=tcp`, `MESHCORE_TCP_HOST`, `MESHCORE_TCP_PORT` | Oui |
| BLE | `MESHCORE_CONNECTION_TYPE=ble`, `MESHCORE_BLE_ADDRESS`, `MESHCORE_BLE_PIN` | Oui |

### Série / USB

```env
MESH_NETWORK=meshcore
MESHCORE_CONNECTION_TYPE=serial
MESHCORE_SERIAL_PORT=/dev/ttyUSB0
MESHCORE_BAUDRATE=115200
```

### TCP

```env
MESH_NETWORK=meshcore
MESHCORE_CONNECTION_TYPE=tcp
MESHCORE_TCP_HOST=192.168.1.100
MESHCORE_TCP_PORT=4000
```

### BLE

```env
MESH_NETWORK=meshcore
MESHCORE_CONNECTION_TYPE=ble
MESHCORE_BLE_ADDRESS=
MESHCORE_BLE_PIN=
```

L’adresse peut rester vide pour laisser la bibliothèque effectuer le scan. Le PIN est facultatif.

## Canaux et messages

MeshCore utilise des messages de canal. Les variables suivantes sont donc des index de canaux MeshCore :

```env
BROADCAST_CHANNEL=0
ALERT_CHANNEL=0
```

Les réponses aux commandes sont envoyées sur le canal MeshCore d’origine lorsque celui-ci est fourni par l’événement reçu. Les messages trop longs sont découpés en parties UTF-8.

## Fonctionnalités MeshCore prises en charge

- réception des événements `CHANNEL_MSG_RECV` ;
- émission avec `send_chan_msg()` ;
- réponses à toutes les commandes communes listées dans [la documentation générale](README.md) ;
- changement de canal avec `!canal` ;
- diffusions météo planifiées ;
- alertes planifiées ;
- connexions Série, TCP et BLE ;
- reconnexion automatique fournie par la bibliothèque ;
- mode simulation ;
- détection automatique du firmware.

MeshCore ne fournit pas les paquets Meshtastic `decoded.position` et `decoded.telemetry` au même format. Les commandes qui nécessitent une position utilisent donc la position par défaut lorsque l’événement MeshCore ne contient pas de GPS.
