"""Plugin to read all messages from all chats/channels/bots"""
import logging
import time

from telethon import events
from telethon.events import NewMessage
from telethon.tl.custom import Dialog
from telethon.tl.types import Channel, Chat, User
from asyncio import sleep

from config import cmd_prefix
from utils import helpers
from utils.client import KantekClient
from utils.mdtex import Bold, Italic, KeyValueItem, MDTeXDocument, Section, SubSection
from config import gban_group

__version__ = '0.0.1'

tlog = logging.getLogger('kantek-channel-log')


@events.register(events.NewMessage(outgoing=True, pattern=f'{cmd_prefix}readall'))
async def readall(event: NewMessage.Event) -> None:
    client: KantekClient = event.client
    waiting_message = await client.respond(event, 'Reading All chats. This might take a while.')
    start_time = time.time()

    async for dialog in client.iter_dialogs():
        entity = dialog.entity

        await client.send_read_acknowledge(entity, clear_mentions=True)

    stop_time = time.time() - start_time

    await client.respond(event, f'Took {stop_time:.02f}s', reply=False)
    await waiting_message.delete()


@events.register(events.NewMessage(outgoing=True, pattern=f'{cmd_prefix}rmmention'))
async def rmmention(event: NewMessage.Event) -> None:
    client: KantekClient = event.client
    waiting_message = await client.respond(event, 'Clearing mentions in your bangroup.')
    for x in range(3):
        await client.send_read_acknowledge(gban_group, clear_mentions=True)
        await sleep(0.5)

    await client.respond(event, 'Done', reply=False)
    await waiting_message.delete()

