import asyncio
import datetime
import logging
from typing import Dict, Optional, List

from telethon.errors import UserNotParticipantError
from telethon.tl.custom import Message, Forward
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.types import (Channel, InputReportReasonSpam, InputPeerChannel, ChannelParticipantCreator,
                               InputMessagesFilterPhotos)

from database.database import Database
from utils import helpers, parsers
from utils.client import Client
from kantex.md import *

from utils.errors import Error
from utils.pluginmgr import k, Command
from utils.tags import Tags

tlog = logging.getLogger('kantek-channel-log')

DEFAULT_REASON = 'spam[gban]'
CHUNK_SIZE = 10


@k.command('fban', delete=True)
async def fwgban(client: Client, db: Database, tags: Tags, chat: Channel, msg: Message,
                 args: List, kwargs: Dict, event: Command) -> Optional[KanTeXDocument]:
    """Globally ban a user.

    This will not actively ban them from any chats except the one command was issued in as reply. GBanned users will be automatically banned on join or when writing a message by the Grenzschutz module.
    When banning by reply the message content will be automatically sent to the SpamWatch API if enabled.

    Arguments:

        `reason`: Ban reason, defaults to `spam[gban]`


    Tags:
        gban:
            verbose: Send a message when a user was banned by id
        gbancmd:
            *: Send `{{bancmd}} {{ban_reason}}` in reply to the message

    Examples (as replies):
        {cmd} "some reason here"
        {cmd}
    """
    _gban = tags.get('gban')
    if event.is_private:
        admin = False
    else:
        admin = bool(chat.creator or chat.admin_rights)
    only_joinspam = kwargs.get('only_joinspam', False) or kwargs.get('oj', False)

    verbose = False
    if _gban == 'verbose' or event.is_private:
        verbose = True

    if msg.is_reply:
        bancmd = tags.get('gbancmd')
        reply_msg: Message = await msg.get_reply_message()
        forward: Forward = reply_msg.forward
        if forward.sender_id is None:
            raise Error('User has forward privacy enabled or is a Channel')

        uid = forward.sender_id
        if args:
            ban_reason = ' '.join(args)
        else:
            ban_reason = DEFAULT_REASON
            try:
                participant = await client(GetParticipantRequest(event.chat_id, reply_msg.from_id))
                if not isinstance(participant.participant, ChannelParticipantCreator):
                    join_date = participant.participant.date

                    if (reply_msg.date - datetime.timedelta(hours=1)) < join_date:
                        ban_reason = 'joinspam'
                    elif only_joinspam:
                        return
            except (UserNotParticipantError, TypeError):
                pass
        banned_uids: Dict = {}
        message = await helpers.textify_message(reply_msg)
        banned, reason = await client.gban(uid, ban_reason, message)
        banned_uids[reason] = banned_uids.get(reason, []) + [str(uid)]
        if verbose:
            sections = []
            if banned_uids:
                bans = _build_message(banned_uids, message)
                sections.append(Section(f'GBanned User', *bans))

            return KanTeXDocument(*sections)



    else:
        pass


def _build_message(bans: Dict[str, List[str]], message: Optional[str] = None) -> List[KeyValueItem]:
    sections = []
    for reason, uids in bans.items():
        sections.append(KeyValueItem(Bold('Reason'), reason))
        sections.append(KeyValueItem(Bold('ID'), Code(', '.join(uids))))
        if message:
            sections.append(KeyValueItem(Bold('Message'), 'Attached'))
    return sections
