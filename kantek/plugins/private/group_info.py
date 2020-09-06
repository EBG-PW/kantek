import logging
from typing import List, Dict, Optional

from kantex.md import *
from telethon.tl.patched import Message
from telethon.tl.types import Channel
from telethon.utils import get_peer_id

from database.database import Database
from utils.client import Client
from utils.constants import GET_ENTITY_ERRORS
from utils.pluginmgr import k
from utils.tags import Tags

tlog = logging.getLogger('kantek-channel-log')


async def _get_valid_ids(chats, client):
    failed = []
    ids = set()
    if chats:
        for c in chats:
            try:
                chat = await client.get_entity(c)
            except GET_ENTITY_ERRORS:
                failed.append(str(c))
                continue

            if isinstance(chat, Channel):
                ids.add(get_peer_id(chat))
            else:
                failed.append(str(c))
    return ids, failed


@k.command('getgroup', 'gg', delete=True)
async def user_info(msg: Message, tags: Tags, client: Client, db: Database,
                    args: List, kwargs: Dict) -> Optional[KanTeXDocument]:
    """Gives info about a chatid.

    Arguments:
        `chats`: Optional list of chat ids and usernames the tags should be set for


    Examples:
        {cmd} -1001129887931

    """
    if args:
        chats, failed = await _get_valid_ids(args, client)
    else:
        chats = {msg.chat_id}
        failed = []

    response: KanTeXDocument = Section('Gruppeninfo')

    for cid in chats:
        tags = await Tags.from_id(db, cid, private=False)

        group_title: Channel = await client.get_entity(cid)

        response.append(SubSection(f'{group_title.title}'))

    if failed:
        tlog.warning(f'Could not set tags for {Code(", ".join(failed))}')
