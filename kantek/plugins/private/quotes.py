import base64
import json
import uuid
from io import BytesIO

import requests
import telethon
from PIL import Image
from telethon import events
from telethon.events import NewMessage

from config import API_TOKEN
from config import cmd_prefix
from utils.client import KantekClient


@events.register(events.NewMessage(outgoing=True, pattern=f'{cmd_prefix}quote'))
async def quote(event: NewMessage.Event) -> None:
    client: KantekClient = event.client
    message = event.message
    colours = ["#fb6169", "#faa357", "#b48bf2", "#85de85", "#62d4e3", "#65bdf3", "#ff5694"]
    reply = await message.get_reply_message()
    if not reply:
        return await client.respond(message, "no_reply")
    profile_photo_url = reply.from_id
    admintitle = ""
    pfp = None
    if isinstance(reply.to_id, telethon.tl.types.PeerChannel) and reply.fwd_from:
        user = reply.forward.chat
    elif isinstance(reply.to_id, telethon.tl.types.PeerChat):
        chat = await client(telethon.tl.functions.messages.GetFullChatRequest(reply.to_id))
        participants = chat.full_chat.participants.participants
        participant = next(filter(lambda x: x.user_id == reply.from_id, participants), None)
        if isinstance(participant, telethon.tl.types.ChatParticipantCreator):
            admintitle = "creator"
        elif isinstance(participant, telethon.tl.types.ChatParticipantAdmin):
            admintitle = "admin"
        user = await reply.get_sender()
    else:
        user = await reply.get_sender()
    username = telethon.utils.get_display_name(user)
    if reply.fwd_from is not None and reply.fwd_from.post_author is not None:
        username += " ({})".format(reply.fwd_from.post_author)
    user_id = reply.from_id
    if reply.fwd_from:
        if reply.fwd_from.saved_from_peer:
            profile_photo_url = reply.forward.chat
            admintitle = "channel"
        elif reply.fwd_from.from_name:
            username = reply.fwd_from.from_name
            profile_photo_url = None
            admintitle = ""
        elif reply.forward.sender:
            username = telethon.utils.get_display_name(reply.forward.sender)
            profile_photo_url = reply.forward.sender.id
            admintitle = ""
        elif reply.forward.chat:
            admintitle = "channel"
            profile_photo_url = user
    else:
        if isinstance(reply.to_id, telethon.tl.types.PeerUser) is False:
            try:
                user = await client(telethon.tl.functions.channels.GetParticipantRequest(message.chat_id,
                                                                                              user))
                if isinstance(user.participant, telethon.tl.types.ChannelParticipantCreator):
                    admintitle = user.participant.rank or "creator"
                elif isinstance(user.participant, telethon.tl.types.ChannelParticipantAdmin):
                    admintitle = user.participant.rank or "admin"
                user = user.users[0]
            except telethon.errors.rpcerrorlist.UserNotParticipantError:
                pass
    if profile_photo_url is not None:
        pfp = await client.download_profile_photo(profile_photo_url, bytes)
    if pfp is not None:
        profile_photo_url = "data:image/png;base64, " + base64.b64encode(pfp).decode()
    else:
        profile_photo_url = ""
    if user_id is not None:
        username_color = colours[user_id % 7]
    else:
        username_color = colours[2]
    reply_username = ""
    reply_text = ""
    reply_to = await reply.get_reply_message()
    if reply_to:
        reply_peer = None
        if reply_to.fwd_from:
            if reply_to.forward.chat:
                reply_peer = reply_to.forward.chat
            elif reply_to.fwd_from.from_id:
                try:
                    user_id = reply_to.fwd_from.from_id
                    user = await client(telethon.tl.functions.users.GetFullUserRequest(user_id))
                    reply_peer = user.user
                except ValueError:
                    pass
            else:
                reply_username = reply_to.fwd_from.from_name
        elif reply_to.from_id:
            reply_user = await client(telethon.tl.functions.users.GetFullUserRequest(reply_to.from_id))
            reply_peer = reply_user.user

        if not reply_username:
            reply_username = telethon.utils.get_display_name(reply_peer)
        reply_text = reply_to.message
    date = ""
    if reply.fwd_from:
        date = reply.fwd_from.date.strftime("%H:%M")
    else:
        date = reply.date.strftime("%H:%M")
    request = json.dumps({
        "ProfilePhotoURL": profile_photo_url,
        "usernameColor": username_color,
        "username": username,
        "adminTitle": admintitle,
        "Text": reply.message,
        "Markdown": [],
        "ReplyUsername": reply_username,
        "ReplyText": reply_text,
        "Date": date,
        "Template": "default",
        "APIKey": API_TOKEN
    })
    respo = requests.post(url="http://api.antiddos.systems/api/v2/quote", data=request)
    resp = respo.json()
    req = requests.get("http://api.antiddos.systems/cdn/" + resp["message"])
    print("http://api.antiddos.systems/cdn/" + resp["message"])
    req.raise_for_status()
    file = BytesIO(req.content)
    file.seek(0)
    img = Image.open(file)
    with BytesIO() as sticker:
            img.save( sticker, "webp")
            sticker.name = "sticker.webp"
            sticker.seek(0)
            sticker_name: str = str(uuid.uuid4())
            img.save(f'Stickersammlung/{sticker_name}.webp', format='WEBP')
            try:
                await client.send_file(entity=event.chat, reply_to=event, file=sticker)
            except telethon.errors.rpcerrorlist.ChatSendStickersForbiddenError:
                await client.respond(message, "cannot_send_stickers")
            file.close()
