from telethon import events
from telethon import events
from telethon.events import NewMessage
from telethon.tl.types import Channel, Chat

from config import cmd_prefix
from utils.client import KantekClient


@events.register(events.NewMessage(outgoing=True, pattern=f'{cmd_prefix}adminlist'))
async def adminlist(event: NewMessage.Event) -> None:
    client: KantekClient = event.client
    waiting_message = await client.respond(event, 'Checking Admin status')
    admin_in_groups = 0
    admin_groups = []
    message = ''

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
        #f'<a href="tg://user?id={uid}">{uid}</a>'
        message += f'<a href="t.me/c/{chat.id}/1000000">{chat.title}</a>' "\n"

    await client.send_message(event.input_chat, message, parse_mode='html')

