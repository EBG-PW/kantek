import logging
from typing import Dict, Union
import asyncio
import logzero
from telethon import events
from telethon.errors import UserIdInvalidError
from telethon.events import ChatAction, NewMessage, UserUpdate
from telethon.tl.types import Channel, ChannelParticipantsAdmins, Chat
from telethon.tl.custom import Message
from utils.client import KantekClient
from config import cmd_prefix
from utils.mdtex import Link
from telethon.sync import TelegramClient
from telethon import functions, types
from Typing import Int

@events.register(events.NewMessage(outgoing=True, pattern=f'{cmd_prefix}adminlist'))
async def adminlist(event: NewMessage.Event) -> None:
    client: KantekClient = event.client
    waiting_message = await client.respond(event, 'Checking Admin status')
    admin_in_groups = 0
    admin_groups = []
    message = ''
    count: Int = 0

    async for dialog in client.iter_dialogs():
        entity = dialog.entity

        if isinstance(entity, Chat):
            if entity.creator or entity.admin_rights:
                admin_in_groups += 1
                admin_groups.append(entity.id)


        if isinstance(entity, Channel):
            if entity.megagroup:
                if entity.creator or entity.admin_rights:
                    admin_in_groups += 1
                    admin_groups.append(entity.id)

    for id in admin_groups:
        chat: Chat = await client.get_entity(id)

        try:
            message += chat.title + str(await functions.messages.ExportChatInviteRequest(id)) + "\n"
            count += 1
        except Exception as e:
            message += "A ERROR OCCURD @GODOFOWLS FIX IT"

        if count == 10:
            await client.respond(event, message)
            message = ''
            count = 0



