""""Plugin to get the fbans of the most important feds of a User."""
import logging
from typing import List

from kantex.md import *
from telethon.errors import MessageIdInvalidError
from telethon.tl.custom import Message
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import Channel, UserFull, InputUser

from utils.client import Client
from utils.pluginmgr import k
from utils.tags import Tags

__version__ = '0.1.2'

tlog = logging.getLogger('kantek-channel-log')


@k.command('globalkick', 'gkick')
async def gkick(msg: Message, tags: Tags, client: Client, db, args: List):
    waiting_message = await client.send_message(msg.chat, 'Starting cleanup. This might take a while.')

    entities: List = []
    for uid in args:
        if isinstance(uid, int):
            entities.append(uid)

    userid: int = entities[0]

    # noinspection PyTypeChecker
    offender: InputUser = await client.get_input_entity(userid)
    offender_full: UserFull = await client(GetFullUserRequest(offender))
    common = offender_full.common_chats_count
    modulus = (common // 2) or 1
    user_counter = 0

    async for dialog in client.iter_dialogs():
        entity = dialog.entity

        if isinstance(entity, Channel):

            chat_tags = await tags.from_id(db, int('-100' + str(entity.id)), private=False)
            print(chat_tags)
            enl = chat_tags.get('enl-only', False)

            if not enl:
                continue

            if not entity.admin_rights or entity.creator:
                continue

            if waiting_message is not None and user_counter % modulus == 0:
                user_counter += 1
                progress = Section('Cleanup',
                                   KeyValueItem(Bold('Progress'),
                                                f'{user_counter}/{common}'))
                try:
                    await waiting_message.edit(str(progress))
                except MessageIdInvalidError:
                    waiting_message = None
            user_counter += 1

            try:
                await client.ban(dialog, userid)
            except Exception as e:
                tlog.critical(e)
