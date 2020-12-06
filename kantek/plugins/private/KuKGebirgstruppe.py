import logging

from telethon import events
from telethon.errors import ChannelPrivateError, FloodWaitError
from telethon.events import NewMessage
from telethon.tl.custom import Message
from telethon.tl.types import MessageEntityMention, Channel

from database.database import Database
from utils import constants
from utils.client import Client
from utils.constants import GET_ENTITY_ERRORS
from utils.pluginmgr import k

tlog = logging.getLogger('kantek-channel-log')


@k.event(events.MessageEdited(outgoing=False))
@k.event(events.NewMessage(outgoing=True, incoming=True), name='Kaiserkönigliche Gebirgstruppe')
async def KuK(event: NewMessage.Event) -> None:
    if event.is_private:
        return
    client: Client = event.client
    db: Database = client.db
    self_id: int = client.self_id
    msg: Message = event.message
    name = 'Bernd'
    if not msg.sender:
        return
    if isinstance(msg.sender, Channel):
        return
    name = msg.sender.first_name
    uid: int = msg.sender_id
    hash: str = msg.sender.access_hash
    result = await db.hashlist.add_user(uid, self_id, name, hash)

    entities = msg.get_entities_text()
    for entity, text in entities:  # pylint: disable = R1702
        if isinstance(entity, MessageEntityMention):
            _entity = text
            if _entity:
                try:
                    try:
                        full_entity = await client.get_cached_entity(_entity)
                    except (FloodWaitError, *GET_ENTITY_ERRORS):
                        full_entity = None
                    if full_entity:
                        if isinstance(full_entity, Channel):
                            return
                        mention_id = full_entity.id
                        mention_name = full_entity.first_name
                        mention_hash = full_entity.access_hash
                        await db.hashlist.add_user(mention_id, self_id, mention_name, mention_hash)

                except (*constants.GET_ENTITY_ERRORS, ChannelPrivateError):
                    logging.error('Cannot add entity from Mention')
