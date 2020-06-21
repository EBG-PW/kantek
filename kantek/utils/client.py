"""File containing the Custom TelegramClient"""
import asyncio
import datetime
import logging
import random
import re
import socket
from typing import Optional, Union, Tuple

import logzero
import spamwatch
from aiohttp import ClientTimeout, ClientSession, ClientError
from faker import Faker
from spamwatch.types import Permission
from telethon import TelegramClient, hints
from telethon.errors import UserAdminInvalidError
from telethon.events import NewMessage, ChatAction
from telethon.tl.custom import Message
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.patched import Message
from telethon.tl.types import ChatBannedRights
from yarl import URL

import config
from database.arango import ArangoDB
from utils.constants import SCHEDULE_DELETION_COMMAND
from utils.mdtex import FormattedBase, MDTeXDocument, Section
from utils.pluginmgr import PluginManager

logger: logging.Logger = logzero.logger

AUTOMATED_BAN_REASONS = ['spambot', 'vollzugsanstalt', 'kriminalamt']
SPAMADD_PATTERN = re.compile(r"spam adding (?P<count>\d+)\+ members")


class KantekClient(TelegramClient):  # pylint: disable = R0901, W0223
    """Custom telethon client that has the plugin manager as attribute."""
    plugin_mgr: Optional[PluginManager] = None
    db: Optional[ArangoDB] = None
    kantek_version: str = ''
    sw: spamwatch.Client = None
    sw_url: str = None
    aioclient: ClientSession = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aioclient = ClientSession(timeout=ClientTimeout(total=2))

    async def respond(self, event: NewMessage.Event,
                      msg: Union[str, FormattedBase, Section, MDTeXDocument],
                      reply: bool = True, delete: Optional[int] = None) -> Message:
        """Respond to the message an event caused or to the message that was replied to

        Args:
            event: The event of the message
            msg: The message text
            reply: If it should reply to the message that was replied to
            delete: Seconds until the sent message should be deleted

        Returns: None

        """
        msg = str(msg)
        if reply:
            if isinstance(event, ChatAction.Event):
                reply_to = event.action_message.id
            else:
                reply_to = (event.reply_to_msg_id or event.message.id)
            sent_msg: Message = await event.respond(msg, reply_to=reply_to)
        else:
            sent_msg: Message = await event.respond(msg, reply_to=event.message.id)
        if delete is not None:
            # While asyncio.sleep would work it would stop the function from returning which is annoying
            await self.send_message(sent_msg.chat, f'{SCHEDULE_DELETION_COMMAND} [Scheduled deletion]',
                                    schedule=datetime.timedelta(seconds=delete), reply_to=sent_msg.id)
        return sent_msg

    async def gban(self, uid: Union[int, str], reason: str, message: Optional[str] = None) -> Tuple[bool, str]:
        """Command to gban a user

        Args:
            uid: User ID
            reason: Ban reason

        Returns:
            True if ban was successful else false, ban reason

        """
        # if the user account is deleted this can be None
        if uid is None:
            return False, 'Deleted account'
        await asyncio.sleep(random.randint(range(10)))
        user = self.db.query('For doc in BanList '
                             'FILTER doc._key == @uid '
                             'RETURN doc', bind_vars={'uid': str(uid)})
        for ban_reason in AUTOMATED_BAN_REASONS:
            if user and (ban_reason in str(user[0]['reason']).lower()):
                if ban_reason == 'kriminalamt':
                    return False, 'Already banned by kriminalamt'
                else:
                    return False, 'Already banned by autobahn'

        if user:
            count = SPAMADD_PATTERN.search(reason)
            previous_count = SPAMADD_PATTERN.search(str(user[0]['reason']))
            if count is not None and previous_count is not None:

                if count == previous_count:
                    return False, 'Already banned'

        data = {'_key': str(uid),
                'id': str(uid),
                'reason': reason}

        self.db.query('UPSERT {"_key": @ban.id} '
                      'INSERT @ban '
                      'UPDATE {"reason": @ban.reason} '
                      'IN BanList ', bind_vars={'ban': data})

        await self.send_message(
            config.gban_group,
            f'<a href="tg://user?id={uid}">{uid}</a>', parse_mode='html')
        await self.send_message(
            config.gban_group,
            f'/ban {uid} {reason}')
        await self.send_message(
            config.gban_group,
            f'/fban {uid} {reason}')
        await asyncio.sleep(2)
        await self.send_read_acknowledge(config.gban_group,
                                         max_id=1000000,
                                         clear_mentions=True)

        data = {'_key': str(uid),
                'id': str(uid),
                'reason': reason}

        self.db.query('UPSERT {"_key": @ban.id} '
                      'INSERT @ban '
                      'UPDATE {"reason": @ban.reason} '
                      'IN BanList ', bind_vars={'ban': data})

        if self.sw and self.sw.permission in [Permission.Admin,
                                              Permission.Root]:
            self.sw.add_ban(int(uid), reason, message)
        # Some bots are slow so wait a while before clearing mentions
        # doesnt really do much, sending a message clears unread messages anyway
        # await asyncio.sleep(10)
        # await self.send_read_acknowledge(config.gban_group,
        #                                  max_id=1000000,
        #                                  clear_mentions=True)

        return True, reason

    async def ungban(self, uid: Union[int, str]):
        """Command to ungban a user

        Args:
            uid: User ID

        Returns: None

        """
        await self.send_message(
            config.gban_group,
            f'<a href="tg://user?id={uid}">{uid}</a>', parse_mode='html')
        await self.send_message(
            config.gban_group,
            f'/ungban {uid}')
        await self.send_message(
            config.gban_group,
            f'/unfban {uid}')
        await self.send_message(
            config.gban_group,
            f'/unban {uid}')
        await asyncio.sleep(0.5)
        await self.send_read_acknowledge(config.gban_group,
                                         max_id=1000000,
                                         clear_mentions=True)

        self.db.query('REMOVE {"_key": @uid} '
                      'IN BanList', bind_vars={'uid': str(uid)})
        if self.sw and self.sw.permission in [Permission.Admin,
                                              Permission.Root]:
            self.sw.delete_ban(int(uid))

    async def ban(self, chat, uid):
        """Bans a user from a chat."""
        try:
            await self(EditBannedRequest(
                chat, uid, ChatBannedRights(
                    until_date=datetime.datetime(2038, 1, 1),
                    view_messages=True
                )
            ))
        except UserAdminInvalidError as err:
            logger.error(err)

    async def get_cached_entity(self, entity: hints.EntitiesLike):
        try:
            input_entity = await self.get_input_entity(entity)
            return await self.get_entity(input_entity)
        except ValueError:
            return None

    async def resolve_url(self, url: str, base_domain: bool = True) -> str:
        """Follow all redirects and return the base domain

        Args:
            url: The url
            base_domain: Flag if any subdomains should be stripped

        Returns:
            The base comain as given by urllib.parse
        """
        faker = Faker()
        headers = {'User-Agent': faker.user_agent()}
        old_url = url
        if not url.startswith('http'):
            url = f'http://{url}'
        try:
            async with self.aioclient.get(url, headers=headers) as response:
                url: URL = response.url
        except (ClientError, asyncio.TimeoutError, socket.gaierror) as err:
            logger.warning(err)
            return old_url

        if base_domain:
            # split up the result to only get the base domain
            # www.sitischu.com => sitischu.com
            url = url.host
            _base_domain = url.split('.', maxsplit=url.count('.') - 1)[-1]
            if _base_domain:
                url = _base_domain
        return str(url)

    async def stalk(self, uid: Union[int, str]) -> bool:
        """Command to start stalking a user

        Args:
            uid: User ID


        Returns:
            True if stalk was successful else false

        """
        # if the user account is deleted this can be None
        if uid is None:
            return False
        user = self.db.query('For doc in StalkList '
                             'FILTER doc._key == @uid '
                             'RETURN doc', bind_vars={'uid': str(uid)})

        self.db.query('UPSERT {"_key": @uid} '
                      ' INSERT{"_key": @uid} '
                      'UPDATE {} IN StalkList', bind_vars={'uid': str(uid)})

        # Some bots are slow so wait a while before clearing mentions
        # doesnt really do much, sending a message clears unread messages anyway
        # await asyncio.sleep(10)
        # await self.send_read_acknowledge(config.gban_group,
        #                                  max_id=1000000,
        #                                  clear_mentions=True)

        return True
