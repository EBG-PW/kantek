"""Plugin that automatically bans according to Sitischus Gban group"""
import logging

from telethon import events

from utils.pluginmgr import k
import logzero
from telethon.events import NewMessage
from telethon.tl.custom import Message
from telethon.tl.types import (Channel, MessageEntityHashtag)
from utils.client import Client

__version__ = '0.1.0'

tlog = logging.getLogger('kantek-channel-log')
logger: logging.Logger = logzero.logger


@k.event(events.NewMessage(outgoing=False), name='spamgrenze')
async def spamgrenze(event: NewMessage.Event) -> None:
    client: Client = event.client
    chat: Channel = await event.get_chat()
    msg: Message = event.message

    if not chat.id == 1302848189:
        return

    if not msg.from_id == 172811422:
        return

    text: str = msg.text

    if not text.startswith('/gban'):
        return

    data: list = text.split(' ', 2)

    userid: int = int(data[1])
    reason: str = data[2]
    if 'Kriminalamt' in reason:
        return

    await client.gban(userid, f'[SW] {reason}')
