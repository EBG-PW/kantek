"""Plugin to manage the autobahn"""
import asyncio
import logging
from html import escape
from typing import Union

import logzero
from telethon import events
from telethon.events import ChatAction
from telethon.events import NewMessage
from telethon.tl.custom import Message
from telethon.tl.types import Channel, User
from telethon.utils import get_display_name

from utils import helpers
from utils.client import Client
from utils.config import Config
from utils.pluginmgr import k
from utils.tags import Tags

tlog = logging.getLogger('kantek-channel-log')
logger: logging.Logger = logzero.logger

log_message_template = '''
A user was detected for spam
Group: <a href="https://t.me/{chat_link}">{chat_title}</a> (#chat{chat_id})
Offender: <a href="tg://user?id={offender_id}">{offender_name}</a> (#ID{offender_id})
Message: <code>{remark}</code>
Anzeige: 
<code>*gban sa: {anzeige}</code>
'''


@k.event(events.MessageEdited(outgoing=False))
@k.event(events.NewMessage(), name='NSHQ')
async def b11bomber(event: Union[ChatAction.Event, NewMessage.Event]) -> None:  # pylint: disable = R0911

    """Automatically log suspicius spam messages

    """
    if event.is_private:
        return

    event: Message
    client: Client = event.client
    chat: Channel = await event.get_chat()
    config = Config()
    db = client.db
    tags = await Tags.from_event(event)
    polizei_tag = tags.get('polizei')
    grenzschutz_tag = tags.get('grenzschutz')
    silent = grenzschutz_tag == 'silent'
    msg = event.message

    user: User = await event.get_sender()
    if polizei_tag == 'exclude':
        return

    if user is None:
        print('None User')
        return

    if chat.id == 1187874753:
        return

    if chat.id == -1001187874753:
        return
    if not chat.megagroup:
        return

    params = {'input': str(msg.text),
              'access_key': config.coffeekey
              }
    try:
        async with client.aioclient.post(f'https://api.intellivoid.net/coffeehouse/v1/nlp/spam_prediction/chatroom',
                                         data=params) as response:

            orig_resp = response
            if orig_resp.content_type != 'application/json':

                return
            response = await response.json()

    except (TimeoutError, asyncio.exceptions.TimeoutError):

        return

    if response['success']:
        if isinstance(user, Channel):
            return
        if user.bot:
            return

        is_spam: bool = response['results']['spam_prediction']['is_spam']
        if is_spam:
            chat_link = getattr(chat, 'username', None) or f'c/{chat.id}'
            data = await helpers.create_strafanzeige(user.id, msg)
            key = await db.strafanzeigen.add(data)
            log_messsage = log_message_template.format(chat_link=f'{chat_link}/{event.id}',
                                                       chat_title=escape(get_display_name(chat)),
                                                       chat_id=chat.id, offender_id=user.id,
                                                       offender_name=escape(get_display_name(user)),
                                                       remark=event.text, anzeige=key)

            await client.send_message(-1001418023497, log_messsage,
                                      parse_mode='html', link_preview=False)
