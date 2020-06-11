"""Plugin to stalk peoples"""
import logging
import socket
from typing import Union

import logzero
from telethon import events
from telethon.events import ChatAction, NewMessage
from telethon.tl.patched import Message
from telethon.tl.types import Channel

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
async def blinky(event: Union[ChatAction.Event, NewMessage.Event]) -> None:
    client: KantekClient = event.client
    chat: Channel = await event.get_chat()
    message: Message = event.message
    db: ArangoDB = client.db
    chat_document = db.groups.get_chat(event.chat_id)
    db_named_tags: Dict = chat_document['named_tags'].getStore()
    espled = db_named_tags.get('espled')

    if espled is not None:
        state = 'e'
    elif message.is_reply:
        state = 'a'
    elif message.media:
        state = 'b'
    elif event.is_private:
        state = 'c'

    else:
        state = 'nix spezielles'

    byte_message = bytes(state, "utf-8")
    opened_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = esp_ip
    port = esp_port
    opened_socket.sendto(byte_message, (ip, port))


@events.register(events.chataction.ChatAction())
async def blinky_chat(event: Union[ChatAction.Event, NewMessage.Event]) -> None:
    client: KantekClient = event.client
    chat: Channel = await event.get_chat()

    if event.user_joined:
        state = 'd'

    else:
        state = 'nix spezielles'

    byte_message = bytes(state, "utf-8")
    opened_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = esp_ip
    port = esp_port
    opened_socket.sendto(byte_message, (ip, port))
