from telethon import events
from telethon.errors import MessageTooLongError
from telethon.events import NewMessage
from config import cmd_prefix


@events.register(events.NewMessage(outgoing=True, pattern=f'{cmd_prefix}json'))
async def json(event: NewMessage.Event) -> None:
    if event.fwd_from:
        return
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        print(previous_message.stringify())
        try:
            await event.edit(previous_message.stringify())
        except MessageTooLongError as e:
            await event.edit(str(e))
    else:
        try:
            await event.edit(event.stringify())
        except MessageTooLongError as e:
            await event.edit(str(e))