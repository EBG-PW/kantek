"""Plugin to log every event because yolo"""
import logging
from typing import Dict

import logzero
from telethon import events

__version__ = '0.4.1'

from telethon.events import NewMessage

from database.arango import ArangoDB
from utils.client import KantekClient

tlog = logging.getLogger('kantek-channel-log')
logger: logging.Logger = logzero.logger


@events.register(events.MessageEdited(outgoing=False))
@events.register(events.NewMessage(outgoing=False))
async def mqtt(event: NewMessage.Event) -> None:

    client: KantekClient = event.client
    db: ArangoDB = client.db
    chat_document = db.groups.get_chat(event.chat_id)
    db_named_tags: Dict = chat_document['named_tags'].getStore()
    no_mqtt = db_named_tags.get('nomqtt')
    if no_mqtt == 'exclude':
        return

    data = {'message': str(event.message),
            'chat_id': str(event.chat_id),
            'message_id': str(event.message.id),
            'message_text': str(event.message.text),
            'sender_id': str(event.message.sender_id)}

    db.query('Insert @event into EventList', bind_vars={'event': data})
