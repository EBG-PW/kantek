import logging

from kantex.md import *
from telethon.tl.custom import Message

from database.database import Database
from utils.client import Client
from utils.pluginmgr import k

tlog = logging.getLogger('kantek-channel-log')

SWAPI_SLICE_LENGTH = 50


@k.command('whitelist', 'wl')
async def whitelist() -> None:
    """Query, Import or Export the banlist."""
    pass


@whitelist.subcommand()
async def query(db: Database, args, kwargs) -> KanTeXDocument:
    """Query the banlist for the total ban count, a specific user or a ban reason.

    If no arguments are provided the total count will be returned.

    If a list of User IDs is provided their ban reasons will be listed next to their ID.

    If a reason is provided the total amount of banned users for that ban reason will be returned.
    Use an asterisk (`*`) as wildcard for ban reasons. For a literal asterisk escape it with a backslash: `\\*`

    Arguments:
        `ids`: User IDs the banlist should be queried for
        `reason`: Ban reasons to count
        `-list`: List users that match the ban reason

    Examples:
        {cmd} 777000 172811422
        {cmd}
    """

    args = [arg for arg in args if isinstance(arg, int)]

    if args:
        query_results = []
        for user in args:
            wl = await db.whitelist.get(user)
            query_results.append(KeyValueItem(user, ('True' if wl else 'False')))


    else:

        query_results = [KeyValueItem(Bold('Total Count'), Code('∞'))]
    return KanTeXDocument(Section('Query Results', *query_results))


@whitelist.subcommand()
async def add(client: Client, db: Database, msg: Message, args) -> KanTeXDocument:
    args = [arg for arg in args if isinstance(arg, int)]

    if args:
        query_results = []
        for user in args:
            wl = await db.whitelist.add(user)
            query_results.append(KeyValueItem(user, ('True' if wl else 'False')))


    else:
        query_results = [KeyValueItem('Success', Bold('FALSE'))]

    return KanTeXDocument(Section('Added to whitelist:', *query_results))
