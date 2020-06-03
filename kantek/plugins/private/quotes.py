import requests
import base64
import json
import telethon

from telethon import events
from config import cmd_prefix

from PIL import Image
from io import BytesIO



@events.register(events.NewMessage(outgoing=True, pattern=f'{cmd_prefix}quote')
async def quote(event: NewMessage.Event) -> None:
    return
    """Quote a message.
    Usage: .quote [template] [file/force_file]
    If template is missing, possible templates are fetched.
    If no args provided, default template will be used, quote sent as sticker"""
    client: KantekClient = event.client
    message = event.message

    USERNAME_COLOURS = ["#fb6169", "#faa357", "#b48bf2", "#85de85",
                                                              "#62d4e3", "#65bdf3", "#ff5694"]


    #args = utils.get_args(message)
    reply = await message.get_reply_message()

    if not reply:
        return await client.respond(message, "no_reply")

    username_color = username = admintitle = user_id = None
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
        username_color = self.config["USERNAME_COLORS"][user_id % 7]
    else:
        username_color = self.config["DEFAULT_USERNAME_COLOR"]

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
                    user = await self.client(telethon.tl.functions.users.GetFullUserRequest(user_id))
                    reply_peer = user.user
                except ValueError:
                    pass
            else:
                reply_username = reply_to.fwd_from.from_name
        elif not reply_to.from_id:
            reply_user = await self.client(telethon.tl.functions.users.GetFullUserRequest(reply_to.from_id))
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
        "Markdown": get_markdown(reply),
        "ReplyUsername": reply_username,
        "ReplyText": reply_text,
        "Date": date,
        "Template": args[0] if len(args) > 0 else "default",
        "APIKey": self.config["API_TOKEN"]
    })

    resp = await utils.run_sync(requests.post, self.config["API_URL"] + "/api/v2/quote", data=request)
    resp.raise_for_status()
    resp = await utils.run_sync(resp.json)

    if resp["status"] == 500:
        return await client.respond(message, "server_error")
    elif resp["status"] == 401:
        if resp["message"] == "ERROR_TOKEN_INVALID":
            return await client.respond(message, "invalid_token")
        else:
            raise ValueError("Invalid response from server", resp)
    elif resp["status"] == 403:
        if resp["message"] == "ERROR_UNAUTHORIZED":
            return await client.respond(message, "unauthorized")
        else:
            raise ValueError("Invalid response from server", resp)
    elif resp["status"] == 404:
        if resp["message"] == "ERROR_TEMPLATE_NOT_FOUND":
            newreq = await utils.run_sync(requests.post, self.config["API_URL"] + "/api/v1/getalltemplates", data={
                "token": self.config["API_TOKEN"]
            })
            newreq = await utils.run_sync(newreq.json)

            if newreq["status"] == "NOT_ENOUGH_PERMISSIONS":
                return await client.respond(message, "not_enough_permissions")
            elif newreq["status"] == "SUCCESS":
                templates = "delimiter".join(newreq["message"])
                return await client.respond(message, "templates".format(templates))
            elif newreq["status"] == "INVALID_TOKEN":
                return await client.respond(message, "invalid_token")
            else:
                raise ValueError("Invalid response from server", newreq)
        else:
            raise ValueError("Invalid response from server", resp)
    elif resp["status"] != 200:
        raise ValueError("Invalid response from server", resp)

    req = await utils.run_sync(requests.get, self.config["API_URL"] + "/cdn/" + resp["message"])
    req.raise_for_status()
    file = BytesIO(req.content)
    file.seek(0)

    if len(args) == 2:
        if args[1] == "file":
            await client.respond(message, file)
        elif args[1] == "force_file":
            file.name = "filename"
            await client.respond(message, file, force_document=True)
    else:
        img = await utils.run_sync(Image.open, file)
        with BytesIO() as sticker:
            await utils.run_sync(img.save, sticker, "webp")
            sticker.name = "sticker.webp"
            sticker.seek(0)
            try:
                await client.respond(message, sticker)
            except telethon.errors.rpcerrorlist.ChatSendStickersForbiddenError:
                await client.respond(message, "cannot_send_stickers")
            file.close()
