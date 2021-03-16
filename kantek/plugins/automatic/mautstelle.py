import logging
import re
import time
from typing import Union, Dict, List, Optional

from kantex.md import *
import logzero
from telethon import events
from telethon.events import ChatAction, NewMessage
from telethon.tl.custom import Message
from telethon.tl.types import (MessageActionChatJoinedByLink,
                               MessageActionChatAddUser, MessageService, User, Channel)


from database.database import Database
from database.types import AddingUser, CountWord
from utils.client import Client
from utils.config import Config
from utils.pluginmgr import k, Command
from utils.tags import Tags

tlog = logging.getLogger('kantek-channel-log')
logger: logging.Logger = logzero.logger




@k.event(events.NewMessage(outgoing=False), name='Asfinag')
async def maut(event: Union[ChatAction.Event, NewMessage.Event]) -> None:  # pylint: disable = R0911
    """Automatically count written words

    This plugin will count wordsand get their overall count.


    """

    client: Client = event.client
    db: Database = client.db

    msg: Message = event.message


    text: str = re.sub('\W+', ' ', msg.text)
    text = text.lower()

    words: list = text.split()
    for word in words:
        await db.wordlist.add(str(word), 1)





@k.command('wordlist', 'cwl')
async def wordl_lister(client: Client, db: Database, tags: Tags, chat: Channel, msg: Message,
               args: List, kwargs: Dict, event: Command) -> Optional[KanTeXDocument]:
    """Query Wordlist.

    This will query the Wordcountlist for written words

    Arguments:
        `words`: List of words you want the count for


    Examples:
        {cmd} eule gurr
        {cmd} eule

    """
    polizei_tag = tags.get('polizei')
    if polizei_tag == 'exclude':
        return


    words_count: dict = {}

    for i in args:
        x: CountWord = await db.wordlist.get(str(i))
        words_count[i] = x.count if x else 0

    data: list = []
    data += [KeyValueItem(key, Code(words_count[key])) for key in words_count]
    return KanTeXDocument(*data)

