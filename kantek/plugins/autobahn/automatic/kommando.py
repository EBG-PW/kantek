import logging
from typing import Union, Dict

import logzero
from kantex.md import *
from telethon import events
from telethon.events import ChatAction, NewMessage
from telethon.tl.types import (MessageActionChatJoinedByLink,
                               MessageActionChatAddUser, MessageService)

from database.database import Database
from utils.client import Client
from utils.pluginmgr import k
from utils.tags import Tags

tlog = logging.getLogger('kantek-channel-log')
logger: logging.Logger = logzero.logger

spammers: Dict = {}


@k.event(events.chataction.ChatAction(), name='KSK')
async def ksk(event: Union[ChatAction.Event, NewMessage.Event]) -> None:  # pylint: disable = R0911
    """Automatically ban spamadding users.

    This plugin will ban spam adding users.

    Tags:
        polizei:
            exclude: Don't log spamadding users
        ksk:
            exclude: Don't log spamadding users
    """
    global spammers
    if event.is_private:
        return

    if isinstance(event, ChatAction.Event):
        if event.user_left or event.user_kicked:
            return

    if isinstance(event, ChatAction.Event):
        if event.action_message is None:
            return
        elif not isinstance(event.action_message.action,
                            (MessageActionChatJoinedByLink, MessageActionChatAddUser)):
            return
    client: Client = event.client
    db: Database = client.db
    tags = await Tags.from_event(event)
    polizei_tag = tags.get('polizei')
    ksk_tag = tags.get('ksk')
    # if ksk_tag == 'exclude' or polizei_tag == 'exclude':
    # return

    msg = event.action_message
    if isinstance(msg, MessageService):
        msg: MessageService
        if isinstance(msg.action, MessageActionChatAddUser):
            action: MessageActionChatAddUser = msg.action
            if msg.sender_id not in action.users:
                uid: int = msg.sender_id

                cnt = spammers.get(uid, 0)
                spammers[uid] = cnt + 1

                current_count = cnt + 1
                print(str(KeyValueItem(uid, current_count)))
                if current_count > 20:
                    if len(spammers) > 200:
                        spammers = {}
                    spammers[msg.from_id] = 0
                    await client.gban(uid, f'spam adding {current_count}+ members')
