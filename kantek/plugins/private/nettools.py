from utils.client import Client
from telethon import events
import asyncio
import io
from utils.pluginmgr import k, Command
from io import StringIO
import traceback
import sys


@k.command('net', document=False)
async def net() -> None:
    """Overlaying Command for network related commands

    .
    """
    pass


@net.subcommand()
async def mtr(event, client: Client, args, kwargs):

    """Get a traceroute to a destination ip

    Examples:
        {cmd} command
    """


    async_process = await asyncio.create_subprocess_shell(
        f'mtr {args[0]} -r -c 20', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await async_process.communicate()
    msg = f"**Traceroute to:** `{args[0]}`\n"
    if stderr.decode():
        msg += f"**Stderr:**\n`{stderr.decode(errors='replace')}`"
    if stdout.decode(errors='replace'):
        msg += f"**Result:**\n`{stdout.decode(errors='replace')}`"
    if len(msg) > 4096:
        with io.BytesIO(bytes(msg, 'utf8')) as file:
            file.name = "mtr_result.txt"
            await client.send_file(
                event.chat_id,
                file,
                force_document=True,
                caption=f'Traceroute to {args[0]}',
                reply_to=event.message.id,
            )
            return

    await client.respond(event, msg)
