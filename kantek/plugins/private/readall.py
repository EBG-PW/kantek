"""Plugin to read all messages from all chats/channels/bots"""
import logging
import time
from asyncio import sleep

from telethon import events
from telethon.events import NewMessage

from config import cmd_prefix
from config import gban_group
from utils.client import KantekClient

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
    for x in range(200):
        await client.send_read_acknowledge(gban_group, clear_mentions=True)
        await sleep(0.5)

    await client.respond(event, 'Done', reply=False)
    await waiting_message.delete()


@events.register(events.NewMessage(outgoing=True, pattern=f'{cmd_prefix}updategroups'))
async def updateer(event: NewMessage.Event) -> None:
    client: KantekClient = event.client
    waiting_message = await client.respond(event,
                                           'Stressing DB')
    start_time = time.time()

    async for dialog in client.iter_dialogs():
        client.db.groups.get_chat(dialog.id)

    stop_time = time.time() - start_time

    await client.respond(event, f'Took {stop_time:.02f}s', reply=False)
    await waiting_message.delete()


@events.register(events.NewMessage(outgoing=True, pattern=f'{cmd_prefix}stress'))
async def countall(event: NewMessage.Event) -> None:
    client: KantekClient = event.client
    waiting_message = await client.respond(event,
                                           'AwangOWO DB')
    start_time = time.time()
    i = 0

    async for dialog in client.iter_dialogs():
        async for message in client.iter_messages(dialog):
            try:
                result = client.db.query('For doc in BanList '
                                         'FILTER doc._key == @id '
                                         'RETURN doc', bind_vars={'id': str(message.sender_id)})
                if not result:
                    print('nope')
                print(str(result))
                i += 1
            except:
                i += 1

    stop_time = time.time() - start_time

    await client.respond(event, f'Took {stop_time:.02f}s and counted {str(i)}', reply=False)
    await waiting_message.delete()


@events.register(events.NewMessage(outgoing=True, pattern=f'{cmd_prefix}db-test'))
async def stressdb(event: NewMessage.Event) -> None:
    client: KantekClient = event.client
    waiting_message = await client.respond(event,
                                           'AwangOWO DBonly')
    start_time = time.time()
    i = 0
    positive = 0

    gesamtzahl = client.db.banlist.count()
    while positive < gesamtzahl:

        result = client.db.query('For doc in BanList '
                                 'FILTER doc._key == @id '
                                 'RETURN doc', bind_vars={'id': str(i)})
        i += 1
        print(f'i ---------- {result}')
        if result:
            positive += 1

    stop_time = time.time() - start_time

    await client.respond(event, f'Took {stop_time:.02f}s and checked {str(i)} entries to find {gesamtzahl} Banns',
                         reply=False)
    await waiting_message.delete()
