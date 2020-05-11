"""Plugin that automatically bans according to a channel"""
import logging

import logzero
from telethon import events
from telethon.events import NewMessage
from telethon.tl.custom import Message
from telethon.tl.types import (Channel, MessageEntityHashtag)

# awful hack until I switch the config to something that isn't python, yes I learned my lesson
try:
    from config import GESTAPO
except ImportError:
    GESTAPO = []

from utils.client import KantekClient

__version__ = '0.1.0'

tlog = logging.getLogger('kantek-channel-log')
logger: logging.Logger = logzero.logger


@events.register(events.NewMessage(chats=GESTAPO))
async def untergrund(event: NewMessage.Event) -> None:
    client: KantekClient = event.client
    chat: Channel = await event.get_chat()
    msg: Message = event.message
    ban: bool = False
    for e, text in msg.get_entities_text():

        if isinstance(e, MessageEntityHashtag):
            if text.startswith('#member_banned'):
                ban = True
                for e, text in msg.get_entities_text():
                    if isinstance(e, MessageEntityHashtag):
                        if text.startswith('#u'):
                            userid = text[2:]
                            await client.gban(userid, f'GESTAPO #{chat.id} No. {msg.id}')







