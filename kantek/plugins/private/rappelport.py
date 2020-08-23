from telethon.tl.custom import Message
from telethon.tl.types import Channel, PeerChannel

from utils.client import Client
from utils.pluginmgr import k
from utils.config import Config
from telethon import TelegramClient


@k.command('report', delete=True)
async def report(client: Client, chat: Channel, msg: Message, args, event):
    config = Config()
    if msg.is_reply:
        reply: Message = await msg.get_reply_message()
        client2: TelegramClient = TelegramClient('reporter', api_id=config.api_id, api_hash=config.api_hash)
        await client2.connect()
        if not await client2.is_user_authorized():
            await client2.start(config.phone_reporter)
        result = await reply.forward_to(-1001187874753)
        async with client2:
            await client2.get_dialogs()

            reported = await client2.forward_messages(messages=result.id, from_peer=PeerChannel(channel_id=1187874753), entity=PeerChannel(channel_id=1275988180))

            print(reported)
    else:
        return
