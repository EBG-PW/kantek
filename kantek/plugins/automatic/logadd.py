from html import escape

import re


from kantex.md import *
from telethon import events
from telethon.errors import MessageIdInvalidError
from telethon.events import NewMessage, ChatAction
from telethon.tl.custom import Message
from telethon.tl.types import Channel, User
from telethon.utils import get_display_name

from utils.client import Client

__version__ = '0.1.0'

from utils.pluginmgr import k
from utils.tags import Tags









@k.event(events.ChatAction, name='logadder')
async def logadder(e: ChatAction) -> None:
    client: Client = e.client
    if not e.user_added:
        return
    me: User = await client.get_entity('me')
    if e.added_by == me:
        return
    a = e.action_message
    if not e.created:
        if me.id not in a.action.users:
            return
    chat: Channel = await e.get_chat()

    adder: User = await e.client.get_entity(a.from_id)
    adder_name = adder.first_name
    chat_link = getattr(chat, 'username', None) or f'c/{chat.id}'
    text = KanTeXDocument(Section('#ADDED',
                                    KeyValueItem('Name', adder_name),
                                    KeyValueItem(Link('Chat', f'https://t.me/{chat_link}/{e.action_message.id}'), chat.title),
                                    KeyValueItem('Adder-ID', adder.id)
                                  ))

    await client.send_message(-1001187874753, str(text))



