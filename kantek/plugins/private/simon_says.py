from typing import List, Dict, Optional

from kantex import KanTeXDocument
from telethon.tl.custom import Message
from telethon.tl.types import Channel

from database.database import Database
from utils.client import Client
from utils.pluginmgr import k, Command
from utils.tags import Tags


@k.command('say', 's', sudos=True)
async def simon_says(client: Client, db: Database, tags: Tags, chat: Channel, msg: Message,
               args: List, kwargs: Dict, event: Command) -> Optional[KanTeXDocument]:


    text: str = msg.raw_text
    new_text = text.split(' ', 1)
    to_send: str = new_text[1]

    await client.send_message(chat, to_send)