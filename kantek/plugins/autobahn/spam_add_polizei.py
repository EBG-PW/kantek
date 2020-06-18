"""Plugin that automatically bans according to a blacklist"""
import logging
from typing import Dict

import logzero
from telethon import events
from telethon.events import ChatAction
from telethon.tl.types import (Channel)

import config
from database.arango import ArangoDB
from utils.client import KantekClient

__version__ = '0.4.1'

tlog = logging.getLogger('kantek-channel-log')
logger: logging.Logger = logzero.logger


@events.register(events.chataction.ChatAction())
async def add_polizei(event: ChatAction.Event) -> None:
    """Plugin to ban users with blacklisted strings in their bio."""
    client: KantekClient = event.client
    chat: Channel = await event.get_chat()
    db: ArangoDB = client.db
    chat_document = db.groups.get_chat(event.chat_id)
    db_named_tags: Dict = chat_document['named_tags'].getStore()
    polizei_tag = db_named_tags.get('polizei')

    if not event.added_by:
        return

    uid: int = event.added_by.id

    result = db.query('For doc in AddList '
                      'FILTER doc._key == @id '
                      'RETURN doc', bind_vars={'id': str(uid)})
    if not result:
        current_amount = 0
    else:
        current_amount = result[0]['count']

    current_amount_int: int = int(current_amount)

    new_amount: int = current_amount_int + 1

    alertlist: list = [5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    #if new_amount in alertlist:
        #await client.send_message(
            #config.log_channel_id,
            #f'Achtung {uid} is spamadding {new_amount} users')

    if new_amount == 100:
        await client.gban(uid, f'spam adding {new_amount}+ members')

    data = {'_key': str(uid),
            'id': str(uid),
            'count': str(new_amount)}

    db.query('UPSERT {"_key": @ban.id} '
             'INSERT @ban '
             'UPDATE {"count": @ban.count} '
             'IN AddList ', bind_vars={'ban': data})
