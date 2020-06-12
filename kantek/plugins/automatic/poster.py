"""Plugin to stalk peoples"""
import logging
from typing import Union

import aiohttp
import logzero
from telethon import events
from telethon.events import ChatAction, NewMessage
from telethon.tl.patched import Message
from telethon.tl.types import Channel, User

from utils.client import KantekClient

try:
    from config import esp_ip, esp_port
except ImportError:
    from config2 import esp_ip, esp_port
from database.arango import ArangoDB
from typing import Dict

logger: logging.Logger = logzero.logger


@events.register(events.MessageEdited())
@events.register(events.NewMessage())
async def poster(event: Union[ChatAction.Event, NewMessage.Event]) -> None:
    return
    client: KantekClient = event.client
    chat: Channel = await event.get_chat()
    message: Message = event.message
    db: ArangoDB = client.db
    chat_document = db.groups.get_chat(event.chat_id)
    db_named_tags: Dict = chat_document['named_tags'].getStore()
    espled = db_named_tags.get('espled')
    user: User = await client.get_entity(event.message.sender_id)
    request = {
        'lauftext': user.first_name,
        'wartenMs': '50',
        'Helligkeit': '5'
    }
    timeout = aiohttp.ClientTimeout(total=2)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:

            async with session.post('http://192.168.20.83', data=request) as lauftext_response:
                print(await lauftext_response.text())

    except Exception as e:

        logger.error(f'Error {str(e)} occured')

