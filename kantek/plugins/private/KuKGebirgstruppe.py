import logging

from telethon import events
from telethon.events import NewMessage
from telethon.tl.custom import Message

from database.database import Database
from utils.client import Client
from utils.pluginmgr import k

tlog = logging.getLogger('kantek-channel-log')


@k.event(events.MessageEdited(outgoing=False))
@k.event(events.NewMessage(outgoing=True, incoming=True), name='Kaiserkönigliche Gebirgstruppe')
async def KuK(event: NewMessage.Event) -> None:
    client: Client = event.client
    db: Database = client.db
    self_id: int = client.self_id
    msg: Message = event.message
    name = 'Bernd'
    name = msg.sender.first_name
    uid: int = msg.sender_id
    hash: str = msg.sender.access_hash
    result = await db.hashlist.add_user(uid, self_id, name, hash)
