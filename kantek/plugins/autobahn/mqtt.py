"""Plugin that automatically bans according to a blacklist"""
import logging
import time
from typing import Dict

import logzero
from telethon import events
from telethon.events import NewMessage
from telethon.tl.types import (Channel)

from database.arango import ArangoDB
from utils.client import KantekClient

__version__ = '0.4.1'

tlog = logging.getLogger('kantek-channel-log')
logger: logging.Logger = logzero.logger


@events.register(events.MessageEdited(outgoing=False))
@events.register(events.NewMessage(outgoing=False))
async def mqttlog(event: NewMessage.Event) -> None:
    """Plugin to automatically ban users for certain messages."""
    client: KantekClient = event.client
    chat: Channel = await event.get_chat()
    db: ArangoDB = client.db
    chat_document = db.groups.get_chat(event.chat_id)
    db_named_tags: Dict = chat_document['named_tags'].getStore()
    exlude = db_named_tags.get('nomqtt', False)
    try:
        from config import mqtt_server, eigenname, mqtt_user, mqtt_password
    except ImportError:
        return

    if not eigenname or not mqtt_server:
        return
    if exlude:
        return

    try:
        import paho.mqtt.client as mqtt
        mqtt = mqtt.Client()
        mqtt.username_pw_set(mqtt_user, password=mqtt_password)
        mqtt.connect(mqtt_server, 1883, 60)
        mqtt.loop_start()

        mqtt.publish('telegram/' + eigenname + '/' + str(event.message.sender.first_name) + ' ' + str(
            event.message.sender.id) + '/' + str(time.time()), str(event.message.text).replace('/', '.'))
        mqtt.disconnect()
    except:
        pass
