from asyncio import subprocess

from utils import helpers
from utils.client import Client
from utils.mdtex import *
from utils.pluginmgr import k, Command
from utils.tags import Tags


@k.command('update')
async def update(client: Client, event: Command, tags: Tags) -> None:
    """Run git pull and exit.

    This command assumes the bot is running under a process manager that automatically restarts it.

    Tags:
        update: Set to `silent` to silence any messages

    Examples:
        {cmd}
    """
    silent = tags.get('update', False)

    # region git pull
    if not silent:
        progess_message = await client.respond(event, MDTeXDocument(
            Section('Updating',
                    f'Running {Code("git pull")}')))
    else:
        await event.delete()

    proc = subprocess.call(['git', 'pull', '-q'])
    if proc != 0:
        msg = MDTeXDocument(
            Section('Error',
                    f'{Code("git")} returned non-zero exit code.',
                    'Please update manually'))
        if not silent:
            await progess_message.edit(str(msg))
        else:
            await client.respond(event, msg)
        return
    # endregion

    # region migrant
    if not silent:
        await progess_message.edit(str(MDTeXDocument(
            Section('Updating',
                    f'Running {Code("migrant apply --all")}'))))
    proc = subprocess.run(['migrant', 'apply', '--all'], stderr=subprocess.PIPE)
    if proc.returncode != 0:
        if b'MigrationComplete' not in proc.stderr:
            msg = MDTeXDocument(
                Section('Error',
                        f'{Code("migrant")} returned non-zero exit code.',
                        'Please update manually'))
            if not silent:
                await progess_message.edit(str(msg))
            else:
                await client.respond(event, msg)
            return
    # endregion

    new_commit = helpers.get_commit()
    if not silent:
        await progess_message.delete()
        await client.respond(
            event,
            MDTeXDocument(
                Section('Updated Kantek',
                        KeyValueItem('New commit', Link(new_commit, helpers.link_commit(new_commit))),
                        Italic('Restarting bot'))))
    await client.disconnect()
