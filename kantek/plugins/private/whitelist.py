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
    """Query,or add to whitelist."""
    pass


@whitelist.subcommand()
async def query(db: Database, args, kwargs) -> KanTeXDocument:
    """Query the white-pride-list for users.


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
    """Add uid's to the white-pride-list


    Examples:
        {cmd} 777000 172811422
    """
    args = [arg for arg in args if isinstance(arg, int)]

    if args:
        query_results = []
        for user in args:
            wl = await db.whitelist.add(user)
            query_results.append(KeyValueItem(user, ('True' if wl else 'False')))


    else:
        query_results = [KeyValueItem('Success', Bold('FALSE'))]

    return KanTeXDocument(Section('Added to whitelist:', *query_results))


@whitelist.subcommand()
async def ag(client: Client, db: Database, msg: Message, args) -> KanTeXDocument:
    """Add all Group members to the whitelist at once"""

    chat = await msg.get_chat()
    query_results = []

    async for user in client.iter_participants(chat):
        wl = await db.whitelist.add(user.id)
        query_results.append(KeyValueItem(user.first_name, ('True' if wl else 'False')))

    return KanTeXDocument(Section('Added to whitelist:', *query_results))
