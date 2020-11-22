import logging

from kantex.md import *
from telethon import events
from telethon.events import NewMessage
from telethon.tl.custom import Message

from database.database import Database
from utils.client import Client
from utils.pluginmgr import k
from utils.tags import Tags

tlog = logging.getLogger('kantek-channel-log')

SWAPI_SLICE_LENGTH = 50


@k.event(events.NewMessage(outgoing=True, incoming=True), name='cuteness listener')
async def cuteness(event: NewMessage.Event) -> None:
    msg: Message = event.message
    client: Client = event.client
    db: Database = client.db
    message_text: str = msg.text
    tags = await Tags.from_event(event)
    loud_cute = tags.get('cute', False)

    if not message_text.startswith('!cute'):
        return

    if not msg.is_reply:
        return

    reply: Message = await msg.get_reply_message()
    lover: int = msg.sender_id
    loved_one: int = reply.sender_id

    adder = await db.cutelist.get(lover)
    if not adder:
        await client.respond(event, str(KanTeXDocument('You need to be cute yourself for first.')))
        return

    loved_already = await db.cutelist.get(loved_one)
    if loved_already:
        prelover = await client.get_entity(loved_already.loved_by)

        if not loud_cute:
            return
        await client.send_message(event.chat,
                                  str(KanTeXDocument(KeyValueItem('Already loved by', prelover.first_name))),
                                  reply_to=msg)
        return

    await db.cutelist.add(loved_one, lover)
