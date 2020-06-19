"""Plugin to get the fbans of the most important feds of a User."""
import asyncio
import logging
from typing import Union

from telethon import events
from telethon.events import NewMessage
from telethon.tl.custom import Forward, Message
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import Channel, MessageEntityMention, MessageEntityMentionName, User, UserFull

from config import cmd_prefix
from utils import helpers, parsers, constants
from utils.client import KantekClient
from utils.mdtex import Bold, Code, KeyValueItem, Link, MDTeXDocument, Section, SubSection

__version__ = '0.1.2'

tlog = logging.getLogger('kantek-channel-log')


@events.register(events.NewMessage(outgoing=True, pattern=f'{cmd_prefix}f(stat)?'))
async def fedcheck(event: NewMessage.Event) -> None:
    chat: Channel = await event.get_chat()
    client: KantekClient = event.client
    msg: Message = event.message

    _args = msg.raw_text.split()[1:]
    keyword_args, args = parsers.parse_arguments(' '.join(_args))
    response = ''

    if not args and msg.is_reply:
        response = await _info_from_reply(event, **keyword_args)
    elif not args and not msg.is_reply and event.is_private:
        response = await _info_from_chat(event)

    elif args or 'search' in keyword_args:
        response = await _info_from_arguments(event)

    if response:
        await client.respond(event, response)


async def _info_from_arguments(event) -> MDTeXDocument:
    msg: Message = event.message
    client: KantekClient = event.client
    keyword_args, args = await helpers.get_args(event)
    search_name = keyword_args.get('search', False)
    if search_name:
        entities = [search_name]
    else:
        entities = [entity[1] for entity in msg.get_entities_text()
                    if isinstance(entity[0], (MessageEntityMention, MessageEntityMentionName))]

    # append any user ids to the list
    for uid in args:
        if isinstance(uid, int):
            entities.append(uid)

    users = []
    errors = []
    for entity in entities:
        try:
            user: User = await client.get_entity(entity)
            user_full: UserFull = await client(GetFullUserRequest(entity))
            users.append(await _collect_user_info(client, user))
        except constants.GET_ENTITY_ERRORS as err:
            errors.append(str(entity))
    if users:
        return MDTeXDocument(*users, (Section(Bold('Errors for'), Code(', '.join(errors)))) if errors else '')


async def _info_from_reply(event, **kwargs) -> MDTeXDocument:
    msg: Message = event.message
    client: KantekClient = event.client
    get_forward = kwargs.get('forward', True)
    reply_msg: Message = await msg.get_reply_message()

    if get_forward and reply_msg.forward is not None:
        forward: Forward = reply_msg.forward
        user: User = await client.get_entity(forward.sender_id)
    else:
        user: User = await client.get_entity(reply_msg.sender_id)

    return MDTeXDocument(await _collect_user_info(client, user))


async def _info_from_chat(event) -> MDTeXDocument:
    msg: Message = event.message
    client: KantekClient = event.client

    user: User = await client.get_entity(msg.to_id)

    return MDTeXDocument(await _collect_user_info(client, user))


async def _collect_user_info(client, user) -> Union[Section, KeyValueItem]:
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
        KeyValueItem('Spam-watch', Code(sw_reason)),
        KeyValueItem('DEAI', Code(deai_reason)),
        KeyValueItem('KARA', Code(kara_reason)),
        KeyValueItem('Rose Support', Code(rose_reason))
    )

    return Section(title, general)
