""""Plugin to get the fbans of the most important feds of a User."""
import asyncio
import logging
from typing import Union, Dict, List, Optional

from telethon.tl.custom import Forward, Message
from telethon.tl.types import MessageEntityMention, MessageEntityMentionName, User


from utils import helpers, constants
from utils.client import Client
from utils.mdtex import *
from utils.pluginmgr import k
from utils.tags import Tags

__version__ = '0.1.2'

tlog = logging.getLogger('kantek-channel-log')


@k.command('fedstat', 'fs')
async def fedcheck(msg: Message, tags: Tags, client: Client, db,
                   args: List, kwargs: Dict) -> Optional[MDTeXDocument]:

    if not args and msg.is_reply:
        return await _info_from_reply(client, msg, db, kwargs, tags)
    elif args:
        return await _info_from_arguments(client, msg, db, args, kwargs)


async def _info_from_arguments(client, msg, db, args, kwargs) -> MDTeXDocument:
    entities = []
    for entity in msg.get_entities_text():
        obj, text = entity
        if isinstance(obj, MessageEntityMentionName):
            entities.append(obj.user_id)
        elif isinstance(obj, MessageEntityMention):
            entities.append(text)
    # append any user ids to the list
    for uid in args:
        if isinstance(uid, int):
            entities.append(uid)

    users = []
    errors = []
    for entity in entities:
        try:
            user: User = await client.get_entity(entity)
            users.append(await _collect_user_info(client, user))
        except constants.GET_ENTITY_ERRORS as err:
            errors.append(str(entity))
    if users:
        return MDTeXDocument(*users, (Section(Bold('Errors for'), Code(', '.join(errors)))) if errors else '')


async def _info_from_reply(client, msg, db, kwargs, tags) -> MDTeXDocument:
    get_forward = kwargs.get('forward', True)
    reply_msg: Message = await msg.get_reply_message()

    if get_forward and reply_msg.forward is not None:
        forward: Forward = reply_msg.forward
        if forward.sender_id is None:
            return MDTeXDocument(Section('Error', 'User has forward privacy enabled'))
        user: User = await client.get_entity(forward.sender_id)
    else:
        user: User = await client.get_entity(reply_msg.sender_id)
    user_section = await _collect_user_info(client, user)
    return MDTeXDocument(user_section)


async def _collect_user_info(client, user) -> Union[str, Section, KeyValueItem]:
    full_name = await helpers.get_full_name(user)

    title = Link(full_name, f'tg://user?id={user.id}')

    async with client.conversation(609517172) as conv:
        # Check Spamwatch ban
        await conv.send_message(f'/fbanstat {user.id} 1c2221d9-aa27-4baf-b77c-8822b36254d2')
        response = await conv.get_response()
        text: str = response.message
        if 'is not banned' in response.message:
            sw_reason = 'Not banned'

        elif 'for the following reason:' in response.message:
            temp = text.split('\n\n')
            reason = temp[1].split('\n\nDate of ban:')
            print(reason)
            sw_reason = reason

        await asyncio.sleep(1)
        # Check Rose Support Official Ban
        await conv.send_message(f'/fbanstat {user.id} 86718661-6bfc-4bd0-9447-7c419eb08e69')
        response = await conv.get_response()
        text: str = response.message
        if 'is not banned' in response.message:
            rose_reason = 'Not banned'

        elif 'for the following reason:' in response.message:
            temp = text.split('\n\n')
            reason = temp[1].split('\n\nDate of ban:')
            rose_reason = reason
            print(reason)

        await asyncio.sleep(1)
        # Check Kara Fed official Ban
        await conv.send_message(f'/fbanstat {user.id} 423680c6-9044-4a4b-92ba-b4e6a36aaec6')
        response = await conv.get_response()
        text: str = response.message
        if 'is not banned' in response.message:
            kara_reason = 'Not banned'

        elif 'for the following reason:' in response.message:
            temp = text.split('\n\n')
            reason = temp[1].split('\n\nDate of ban:')
            print(reason)
            kara_reason = reason

        await asyncio.sleep(1)
        # Check de_ai Ban
        await conv.send_message(f'/fbanstat {user.id} 9477362a-9209-4389-844a-395986b13b0e')
        response = await conv.get_response()
        text: str = response.message
        if 'is not banned' in response.message:
            deai_reason = 'Not banned'

        elif 'for the following reason:' in response.message:
            temp = text.split('\n\n')
            reason = temp[1].split('\n\nDate of ban:')
            deai_reason = reason

    general = SubSection(
        Bold('general'),
        KeyValueItem('id', Code(user.id)),
        KeyValueItem('SpamWatch', Code(sw_reason)),
        KeyValueItem('DEAI', Code(deai_reason)),
        KeyValueItem('KARA', Code(kara_reason)),
        KeyValueItem('Rose Support', Code(rose_reason))
    )

    return Section(title, general)
