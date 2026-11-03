# Backend Meshtastic

Le backend Meshtastic est implémenté dans `bot/meshtastic_client.py` et utilise la bibliothèque Python `meshtastic`.

## Transports disponibles

| Transport | Variable | Disponible |
|---|---|---:|
| Série / USB | `MESHTASTIC_CONNECTION_TYPE=serial` | Oui |
| TCP | `MESHTASTIC_CONNECTION_TYPE=tcp` | Oui |
| BLE | `MESHTASTIC_CONNECTION_TYPE=ble` | Non dans l’adaptateur actuel |

### Série / USB

```env
MESH_NETWORK=meshtastic
MESHTASTIC_CONNECTION_TYPE=serial
MESHTASTIC_SERIAL_PORT=/dev/ttyUSB0
```

Sous Windows, utilisez par exemple `COM3`. Selon le matériel, le port peut être `/dev/ttyACM0` sous Linux ou `/dev/cu.usbmodem...` sous macOS.

### TCP

```env
MESH_NETWORK=meshtastic
MESHTASTIC_CONNECTION_TYPE=tcp
MESHTASTIC_TCP_HOST=192.168.1.100
```

## Options radio communes

Les index sont ceux des canaux Meshtastic :

```env
BROADCAST_CHANNEL=0
ALERT_CHANNEL=0
```

`!canal 2` modifie le canal utilisé par les diffusions météo périodiques. Les alertes utilisent `ALERT_CHANNEL`.

## Fonctionnalités Meshtastic prises en charge

- réception et émission de messages texte ;
- réponses aux commandes communes ;
- messages directs ou diffusés via l’API Meshtastic ;
- lecture de la position GPS d’un paquet entrant ;
- réception de télémétrie environnementale BME280 ;
- mode simulation ;
- détection automatique par repli depuis MeshCore.

Le BLE Meshtastic n’est pas sélectionnable actuellement : si cette fonction est nécessaire, utilisez une connexion TCP ou série, ou forcez une évolution de l’adaptateur.
