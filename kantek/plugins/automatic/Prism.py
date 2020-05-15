"""Plugin to manage the autobahn"""
import logging
from typing import Dict, Union

import logzero
from telethon import events
from telethon.errors import UserIdInvalidError
from telethon.events import ChatAction, NewMessage, UserUpdate
from telethon.tl.types import Channel, ChannelParticipantsAdmins
from config import StalkingGroup

from database.arango import ArangoDB
from utils.client import KantekClient
from utils.mdtex import Bold, Code, KeyValueItem, MDTeXDocument, Mention, Section


@events.register(events.UserUpdate)
@events.register(events.chataction.ChatAction())
@events.register(events.NewMessage())
async def prism(event: Union[ChatAction.Event, NewMessage.Event]) -> None:
    """Plugin to ban blacklisted users."""

    client: KantekClient = event.client
    chat: Channel = await event.get_chat()
    db: ArangoDB = client.db

    if isinstance(event, ChatAction.Event):
        uid = event.user_id
    elif isinstance(event, NewMessage.Event):
        uid = event.message.from_id
    elif isinstance(event, UserUpdate.Event):
        uid = event.user_id
    else:
        return
    if uid is None:
        return
    try:
        user = await client.get_entity(uid)
    except ValueError as err:
        logger.error(err)

    result = db.query('For doc in StalkList '
                      'FILTER doc._key == @id '
                      'RETURN doc', bind_vars={'id': str(uid)})
    if not result:
        return
    else:
        if event.online:
            await client.send_message(
            StalkingGroup,
            f'<a href="tg://user?id={uid}">{uid}</a> went online', parse_mode='html')

