''''"""Plugin that automatically bans for CAS"""
import logging

import logzero
from telethon import events
from telethon.events import NewMessage
from telethon.tl.custom import Message
from telethon.tl.types import MessageEntityTextUrl
from utils.client import KantekClient
import re

__version__ = '0.1.0'

tlog = logging.getLogger('kantek-channel-log')
logger: logging.Logger = logzero.logger


@events.register(events.NewMessage(chats="https://t.me/cas_feed"))
async def austria(event: NewMessage.Event) -> None:
    client: KantekClient = event.client
    msg: Message = event.message

    for e, text in msg.get_entities_text():

        if isinstance(e, MessageEntityTextUrl):

            regex = r"(?<=\=).*"
            matches = re.finditer(regex, e.url, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):

                userid = match.group()
                await client.gban(userid, f'Cobra cas.chat/query?u={userid}')
                print("banner")
'''