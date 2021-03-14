# Plugin by Dank-Del

from utils.client import Client
from telethon import events
import asyncio
import io
from utils.pluginmgr import k, Command
from io import StringIO
import traceback
import sys


@k.command('shell')
async def term(event, client: Client):
    """Run terminal cmds from Kantek itself

    Examples:
        {cmd} command
    """

    if event.fwd_from:
        return
    cmd = event.text.split(" ", 1)
    if len(cmd) == 1:
        return
    else:
        cmd = cmd[1]
    async_process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await async_process.communicate()
    msg = f"**Command:**\n`{cmd}`\n"
    if stderr.decode():
        msg += f"**Stderr:**\n`{stderr.decode(errors='replace')}`"
    if stdout.decode(errors='replace'):
        msg += f"**Stdout:**\n`{stdout.decode(errors='replace')}`"
    if len(msg) > 4096:
        with io.BytesIO(bytes(msg, 'utf8')) as file:
            file.name = "shell.txt"
            await client.send_file(
                event.chat_id,
                file,
                force_document=True,
                caption=cmd,
                reply_to=event.message.id,
            )
            return
    await event.edit(msg)


# Thanks to stackoverflow for existing https://stackoverflow.com/questions/3906232/python-get-the-print-output-in-an-exec-statement


@k.command('eval')
async def evaluate(event):
    """Evaluate stuff with python

    Examples:
        {cmd}
    """
    split = event.text.split(" ", 1)
    if len(split) == 1:
        await event.edit("Wot")
        return
    try:
        evaluation = eval(split[1])
    except Exception as e:
        evaluation = e
    await event.edit(str(evaluation))


@k.command('exec')
async def execute(event):
    """Execute python code

    Examples:
        {cmd}
    """
    split = event.text.split(" ", 1)
    if len(split) == 1:
        await event.send("Wot")
        return
    stderr, output, wizardry = None, None, None
    code = split[1]
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    try:
        await async_exec(code, event)
    except Exception:
        wizardry = traceback.format_exc()
    output = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    final = f"Command:\n`{code}`\n"
    sys.stderr = old_stderr
    if wizardry:
        final += "**Output**:\n`" + wizardry
    elif output:
        final += "**Output**:\n`" + output
    elif stderr:
        final += "**Output**:\n`" + stderr
    else:
        final = "`OwO no output"
    if len(final) >= 4096:
        with open("output.txt", "w+") as file:
            file.write(final)
        await Client.send_file(event.chat_id, "output.txt", caption=code)
        return
    await event.edit(final + "`")


async def async_exec(code, event):
    exec(
        f"async def __async_exec(event): "
        + "".join(f"\n {l}" for l in code.split("\n"))
    )
    return await locals()["__async_exec"](event)
