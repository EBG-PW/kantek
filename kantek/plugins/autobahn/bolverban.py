import asyncio
import datetime
import logging
from typing import Dict, Optional, List

from telethon.errors import UserNotParticipantError
from telethon.tl import custom

from telethon.tl.custom import Message
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.types import (Channel, InputReportReasonSpam, InputPeerChannel, ChannelParticipantCreator,
                               InputMessagesFilterPhotos, User)

from database.database import Database
from utils import helpers, parsers
from utils.client import Client
from kantex.md import *
from utils.pluginmgr import k, Command
from utils.tags import Tags

tlog = logging.getLogger('kantek-channel-log')

DEFAULT_REASON = 'spam[gban]'
CHUNK_SIZE = 10


@k.command('bban', delete=True)
async def bban(client: Client, db: Database, tags: Tags, chat: Channel, msg: Message,
               args: List, kwargs: Dict, event: Command) -> Optional[KanTeXDocument]:
    """Globally ban a user.

    This will call the joinprotectbot function to gban a user in the Bolverwatch Network



    """

    if msg.is_reply:

        reply_msg: Message = await msg.get_reply_message()

        uid = reply_msg.from_id

        offender: User = await client.get_entity(uid)

        # Make an inline query to @like
        results: custom.inlineresults = await client.inline_query('JoinProtectionBot',
                                                                  f'gban {uid} {offender.username if offender.username else offender.first_name}')
        haftbefehl: custom.InlineResult = results[0]

        message = await haftbefehl.click(chat, reply_to=reply_msg)


    else:
        return KanTeXDocument(Section('Error', SubSection(Code('Not an reply'))))


@k.command('btoken', delete=False)
async def bban(client: Client, db: Database, tags: Tags, chat: Channel, msg: Message,
               args: List, kwargs: Dict, event: Command) -> Optional[KanTeXDocument]:
    """Globally ban a user.

    This will call the joinprotectbot function to tokenize a user in the Bolverwatch Network



    """

    if msg.is_reply:

        reply_msg: Message = await msg.get_reply_message()

        uid = reply_msg.from_id

        offender: User = await client.get_entity(uid)

        # Make an inline query to @like
        results: custom.inlineresults = await client.inline_query('JoinProtectionBot', f'token {uid}')
        haftbefehl: custom.InlineResult = results[0]

        message = await haftbefehl.click(chat, reply_to=reply_msg)

    else:
        return KanTeXDocument(Section('Error', SubSection(Code('Not an reply'))))
