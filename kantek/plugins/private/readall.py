"""Plugin to read all messages from all chats/channels/bots"""
import logging
import time

from telethon import events
from telethon.events import NewMessage
from telethon.tl.custom import Dialog
from telethon.tl.types import Channel, Chat, User

from config import cmd_prefix
from utils import helpers
from utils.client import KantekClient
from utils.mdtex import Bold, Italic, KeyValueItem, MDTeXDocument, Section, SubSection

__version__ = '0.0.1'

tlog = logging.getLogger('kantek-channel-log')


@events.register(events.NewMessage(outgoing=True, pattern=f'{cmd_prefix}readall'))
async def readall(event: NewMessage.Event) -> None:
    client: KantekClient = event.client
    waiting_message = await client.respond(event, 'Reading All chats. This might take a while.')
    start_time = time.time()

    async for dialog in client.iter_dialogs():
        entity = dialog.entity

        await client.send_read_acknowledge(entity)

    stop_time = time.time() - start_time

    await client.respond(event, 'Took' + stop_time, reply=False)
    await waiting_message.delete()