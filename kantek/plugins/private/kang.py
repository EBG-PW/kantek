from telethon import events
from telethon.events import NewMessage
from utils.client import KantekClient
from config import cmd_prefix
import math
import io
from PIL import Image
from telethon.tl.types import DocumentAttributeFilename, MessageMediaPhoto
import urllib.request
from io import BytesIO

PACK_FULL = "Whoa! That's probably enough stickers for one pack, give it a break. \
A pack can't have more than 120 stickers at the moment."

@events.register(events.NewMessage(outgoing=True, pattern=f'{cmd_prefix}kang'))
async def kang(event: NewMessage.Event) -> None:
    client: KantekClient = event.client
    user = await client.get_me()
    if not user.username:
        user.username = user.first_name
    message = await event.get_reply_message()
    photo = None
    emojibypass = False
    is_anim = False
    emoji = ""
    await event.edit("`Kanging..........`")
    if message and message.media:
        if isinstance(message.media, MessageMediaPhoto):
            photo = io.BytesIO()
            photo = await client.download_media(message.photo, photo)
        elif "image" in message.media.document.mime_type.split('/'):
            photo = io.BytesIO()
            await client.download_file(message.media.document, photo)
            if (DocumentAttributeFilename(file_name='sticker.webp') in
                    message.media.document.attributes):
                emoji = message.media.document.attributes[1].alt
                emojibypass = True
        elif (DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in
              message.media.document.attributes):
            emoji = message.media.document.attributes[0].alt
            emojibypass = True
            is_anim = True
            photo = 1
        else:
            await event.edit("`Unsupported File!`")
            return
    else:
        await event.edit("`Reply to photo to kang it bruh`")
        return

    if photo:
        splat = event.text.split()
        if not emojibypass:
            emoji = "🤔"
        pack = 1
        if len(splat) == 3:
            pack = splat[2]  # User sent both
            emoji = splat[1]
        elif len(splat) == 2:
            if splat[1].isnumeric():
                # User wants to push into different pack, but is okay with
                # thonk as emote.
                pack = int(splat[1])
            else:
                # User sent just custom emote, wants to push to default
                # pack
                emoji = splat[1]

        packname = f"a{user.id}_by_{user.username}_{pack}"
        packnick = f"@{user.username}'s userbot pack {pack}"
        cmd = '/newpack'
        file = io.BytesIO()

        if not is_anim:
            image = await resize_photo(photo)
            file.name = "sticker.png"
            image.save(file, "PNG")
        else:
            packname += "_anim"
            packnick += " animated"
            cmd = '/newanimated'

        response = urllib.request.urlopen(
            urllib.request.Request(f'http://t.me/addstickers/{packname}'))
        htmlstr = response.read().decode("utf8").split('\n')

        if "  A <strong>Telegram</strong> user has created the <strong>Sticker&nbsp;Set</strong>." not in htmlstr:
            async with client.conversation('Stickers') as conv:
                await conv.send_message('/addsticker')
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await client.send_read_acknowledge(conv.chat_id)
                await conv.send_message(packname)
                x = await conv.get_response()
                while x.text == PACK_FULL:
                    pack += 1
                    packname = f"a{user.id}_by_{user.username}_{pack}"
                    packnick = f"@{user.username}'s userbot pack {pack}"
                    await event.edit("`Switching to Pack " + str(pack) +
                                    " due to insufficient space`")
                    await conv.send_message(packname)
                    x = await conv.get_response()
                    if x.text == "Invalid pack selected.":
                        await conv.send_message(cmd)
                        await conv.get_response()
                        # Ensure user doesn't get spamming notifications
                        await client.send_read_acknowledge(conv.chat_id)
                        await conv.send_message(packnick)
                        await conv.get_response()
                        # Ensure user doesn't get spamming notifications
                        await client.send_read_acknowledge(conv.chat_id)
                        if is_anim:
                            await client.forward_messages('Stickers',
                                                       [message.id],
                                                       event.chat_id)
                        else:
                            file.seek(0)
                            await conv.send_file(file, force_document=True)
                        await conv.get_response()
                        await conv.send_message(emoji)
                        # Ensure user doesn't get spamming notifications
                        await client.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await conv.send_message("/publish")
                        if is_anim:
                            await conv.get_response()
                            await conv.send_message(f"<{packnick}>")
                        # Ensure user doesn't get spamming notifications
                        await conv.get_response()
                        await client.send_read_acknowledge(conv.chat_id)
                        await conv.send_message("/skip")
                        # Ensure user doesn't get spamming notifications
                        await client.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await conv.send_message(packname)
                        # Ensure user doesn't get spamming notifications
                        await client.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        # Ensure user doesn't get spamming notifications
                        await client.send_read_acknowledge(conv.chat_id)
                        await event.edit(
                            f"Sticker added in a Different Pack! This Pack is Newly created! Your pack can be found [here](t.me/addstickers/{packname})",
                            parse_mode='md')
                        return
                if is_anim:
                    await client.forward_messages('Stickers', [message.id],
                                               event.chat_id)
                else:
                    file.seek(0)
                    await conv.send_file(file, force_document=True)
                await conv.get_response()
                await conv.send_message(emoji)
                # Ensure user doesn't get spamming notifications
                await client.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message('/done')
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await client.send_read_acknowledge(conv.chat_id)
        else:
            await event.edit("Userbot sticker pack \
    doesn't exist! Making a new one!")
            async with client.conversation('Stickers') as conv:
                await conv.send_message(cmd)
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await client.send_read_acknowledge(conv.chat_id)
                await conv.send_message(packnick)
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await client.send_read_acknowledge(conv.chat_id)
                if is_anim:
                    await client.forward_messages('Stickers', [message.id],
                                               event.chat_id)
                else:
                    file.seek(0)
                    await conv.send_file(file, force_document=True)
                await conv.get_response()
                await conv.send_message(emoji)
                # Ensure user doesn't get spamming notifications
                await client.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message("/publish")
                if is_anim:
                    await conv.get_response()
                    await conv.send_message(f"<{packnick}>")
                # Ensure user doesn't get spamming notifications
                await conv.get_response()
                await client.send_read_acknowledge(conv.chat_id)
                await conv.send_message("/skip")
                # Ensure user doesn't get spamming notifications
                await client.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message(packname)
                # Ensure user doesn't get spamming notifications
                await client.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await client.send_read_acknowledge(conv.chat_id)

        await event.edit(
            f"Sticker added! Your pack can be found [here](t.me/addstickers/{packname})",
            parse_mode='md')

@events.register(events.NewMessage(outgoing=True, pattern=f'{cmd_prefix}resize_photo'))
async def resize_photo(photo):
    """ Resize the given photo to 512x512 """
    image = Image.open(photo)
    maxsize = (512, 512)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        image = image.resize(sizenew)
    else:
        image.thumbnail(maxsize)

    return image