"""Plugin to manage the autobahn"""
import logging
from typing import Union

import logzero
from spamwatch.client import Client as SWOClient
from telethon import events
from telethon.errors import UserIdInvalidError
from telethon.events import ChatAction, NewMessage
from telethon.tl.types import (Channel, ChannelParticipantsAdmins, MessageActionChatJoinedByLink,
                               MessageActionChatAddUser)


from utils.client import Client
from utils.config import Config
from utils.mdtex import *
from utils.pluginmgr import k
from utils.tags import Tags

tlog = logging.getLogger('kantek-channel-log')
logger: logging.Logger = logzero.logger


@k.event(events.chataction.ChatAction())
@k.event(events.NewMessage(), name='spamschutz')
async def spamschutz(event: Union[ChatAction.Event, NewMessage.Event]) -> None:  # pylint: disable = R0911

    """Automatically gban spamwatch banned users.

    This plugin gban users banned in Spamwatch upon joining,getting added to the group or when writing a message. A message will be sent to notify Users of the action, this message will be deleted after 2 minutes.

    Tags:
        polizei:
            exclude: Don't ban spamwatched users
        grenschutz:
            silent: Don't send the notification message
            exclude: Don't ban spamwatched users
    """
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
    chat: Channel = await event.get_chat()
    config = Config()
    db = client.db
    swoclient = client.swo
    tags = await Tags.create(event)
    polizei_tag = tags.get('polizei')
    grenzschutz_tag = tags.get('grenzschutz')
    silent = grenzschutz_tag == 'silent'

    if isinstance(event, ChatAction.Event):
        uid = event.user_id
    elif isinstance(event, NewMessage.Event):
        uid = event.message.from_id
    else:
        return
    if uid is None:
        return

    ban = swoclient.get_ban(uid)
    if not ban:
        result = await db.banlist.get(uid)
        if not result:
            return
        else:
            ban_reason = result.reason

            if '[SW]' in ban_reason:
                await client.ungban(uid)
                return

            else:
                return

    reason = '[SW] ' + ban.reason

    await client.gban(uid, reason)

    if grenzschutz_tag == 'exclude' or polizei_tag == 'exclude':
        return

    if not chat.creator and not chat.admin_rights:
        return
    if chat.admin_rights:
        if not chat.admin_rights.ban_users:
            return

    admins = [p.id for p in await client.get_participants(event.chat_id, filter=ChannelParticipantsAdmins())]
    if uid not in admins:
        try:
            await client.ban(chat, uid)
        except UserIdInvalidError as err:
            logger.error("Error occured while banning %s", err)
            return
        await event.delete()
        if not silent:
            try:
                user = await client.get_entity(uid)
                message = MDTeXDocument(Section(
                    Bold('SpamSchutz Grenzschutz Ban'),
                    KeyValueItem(Bold("User"),
                                 f'{Mention(user.first_name, uid)} [{Code(uid)}]'),
                    KeyValueItem(Bold("Reason"),
                                 reason)
                ))
                await client.respond(event, str(message), reply=False, delete=120)

            except ValueError as err:
                logger.error(err)
