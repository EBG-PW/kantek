"""Plugin to manage the autobahn"""
import asyncio
import base64
import logging
from html import escape
from io import BytesIO
from typing import Union

import PIL.Image
import logzero
from PIL import Image
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



@k.event(events.MessageEdited(outgoing=False))
@k.event(events.NewMessage(), name='NSHQ')
async def uboot(event: Union[ChatAction.Event, NewMessage.Event]) -> None:  # pylint: disable = R0911

    """Automatically log NSFW images

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


    if not msg.photo:
        return

    try:
        input_pic = await client.download_file(msg.photo)
    except TypeError:
        return

    pil_photo: PIL.Image = Image.open(BytesIO(input_pic))
    im_file = BytesIO()
    pil_photo.save(im_file, format="JPEG")
    im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
    pic = base64.b64encode(im_bytes)


    params = {'image': pic.decode(),
              'access_key': config.coffeekey
              }
    try:
        async with client.aioclient.post(f'https://api.intellivoid.net/coffeehouse/v1/image/nsfw_classification',
                                         data=params) as response:

            orig_resp = response
            if orig_resp.content_type != 'application/json':

                return
            response = await response.json()

    except (TimeoutError, asyncio.exceptions.TimeoutError):

        return

    if response['results']['nsfw_classification']['is_nsfw']:
        x = await event.forward_to(config.log_channel_id)
        await client.send_message(config.log_channel_id, '#NSFW', reply_to=x)
