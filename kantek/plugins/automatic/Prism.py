"""Plugin to stalk peoples"""
import asyncio
import logging
from typing import Union

import logzero
from telethon import events
from telethon.events import ChatAction, NewMessage, UserUpdate
from telethon.tl.custom import Message
from telethon.tl.types import Channel

from config import StalkingGroup
from config import cmd_prefix
from database.arango import ArangoDB
from utils import helpers
from utils.client import KantekClient

logger: logging.Logger = logzero.logger


@events.register(events.NewMessage(outgoing=True, pattern=f'{cmd_prefix}stalk'))
async def hawk(event: NewMessage.Event) -> None:
    """Command to stalk a user."""

    chat: Channel = await event.get_chat()
    msg: Message = event.message
    client: KantekClient = event.client
    keyword_args, args = await helpers.get_args(event)

    await msg.delete()
    if msg.is_reply:

        reply_msg: Message = await msg.get_reply_message()
        uid = reply_msg.from_id
        if args:
            ban_reason = args[0]

        await client.stalk(uid)

    else:
        uids = []
        for arg in args:
            if isinstance(arg, int):
                uids.append(arg)
        while uids:

            for uid in uids:
                banned = await client.stalk(uid)


@events.register(events.UserUpdate())
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
        await asyncio.sleep(5)

    result = db.query('For doc in StalkList '
                      'FILTER doc._key == @id '
                      'RETURN doc', bind_vars={'id': str(uid)})
    if not result:
        return
    else:
        """
        if event.online :
            await client.send_message(
                StalkingGroup,
                f'<a href="tg://user?id={uid}">{uid}</a> went online', parse_mode='html')
            return
        if event.uploading:
            await client.send_message(
                StalkingGroup,
                f'<a href="tg://user?id={uid}">{uid}</a> is sending a file', parse_mode='html')
            return

        if event.typing:
            await client.send_message(
                StalkingGroup,
                f'<a href="tg://user?id={uid}">{uid}</a> is typing in <a href="tg://user?id={chat}">{chat}</a>', parse_mode='html')
            return

                    


        await client.send_message(
            StalkingGroup,
                f'<a href="tg://user?id={uid}">{uid}</a> {str(event)}', parse_mode='html') """

        if isinstance(event, ChatAction.Event):
            uid = event.user_id
        elif isinstance(event, NewMessage.Event):
            uid = event.message.from_id
            await client.send_message(
                StalkingGroup,
                f'<a href="tg://user?id={uid}">{user.first_name}</a> schrieb eine Nachricht <a href="t.me/c/{chat.id}/{event.message.id}">{str(chat.title)}</a>',
                parse_mode='html')
            return
        elif isinstance(event, UserUpdate.Event):
            uid = event.user_id
            print(str(event))
            if event.typing is True:
                '''
                await client.send_message(
                    StalkingGroup,
                    f'<a href="tg://user?id={uid}">{user.first_name}</a> is typing in <a href="t.me/c/{chat.id}/10000000">{str(chat.title)}</a>',
                    parse_mode='html')
                '''
                return
