from html import escape

import re
from telethon import events
from telethon.errors import MessageIdInvalidError
from telethon.events import NewMessage, chataction
from telethon.tl.custom import Message
from telethon.tl.types import Channel, User
from telethon.utils import get_display_name

from utils.client import Client

__version__ = '0.1.0'

from utils.pluginmgr import k
from utils.tags import Tags









@k.event(events.ChatAction, name='logadder')
async def admin_reports(e: chataction.Event) -> None:
    if (not e.user_added) and (not e.created):
        return
    me = await e.client.get_peer_id('me')
    if e.added_by == me:
        return
    a = e.action_message
    if not e.created:
        if me not in a.action.users:
            return
    chat = await #Hier den chat getten
#    print(a.stringify())
    adder: User = await e.client.get_entity(a.from_id)
    adder_name = adder.first_name
    text = #Hier ein ordentlicher String mit chat adder und addername

    await e.client.send_message(config.log_chat, text) #Hier den text in die log group schicken

