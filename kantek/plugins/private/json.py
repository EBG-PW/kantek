from telethon.errors import MessageTooLongError
from utils.client import Client
from utils.pluginmgr import k, Command

@k.command('json')
async def json(client: Client, event: Command) -> None:
    """Display Data of replyed message in json

    Examples:
        {cmd}
    """
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