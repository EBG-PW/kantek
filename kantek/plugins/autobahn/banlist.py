import asyncio
import codecs
import csv
import logging
import os
import time
from io import BytesIO

from kantex.md import *
from spamwatch.types import Ban, Permission
from telethon.tl.custom import Message
from telethon.tl.types import DocumentAttributeFilename, Channel

from database.database import Database
from utils import helpers
from utils.client import Client
from utils.errors import Error
from utils.pluginmgr import k

tlog = logging.getLogger('kantek-channel-log')

SWAPI_SLICE_LENGTH = 50
CHUNK_SIZE = 10

@k.command('banlist', 'bl')
async def banlist() -> None:
    """Query, Import or Export the banlist."""
    pass


@banlist.subcommand()
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
        {cmd} reason: "spam[gban]"
        {cmd} reason: "Kriminalamt *"
        {cmd}
    """
    reason = kwargs.get('reason')
    list_ids = kwargs.get('list')
    args = [arg for arg in args if isinstance(arg, int)]

    if args:
        users = await db.banlist.get_multiple(args)
        query_results = [KeyValueItem(Code(user.id), user.reason)
                         for user in users] or [Italic('None')]
    elif reason is not None and not list_ids:
        count: int = await db.banlist.count_reason(reason)
        query_results = [KeyValueItem(Bold('Count'), Code(count))]
    elif reason is not None and list_ids:
        bans = await db.banlist.get_with_reason(reason)
        query_results = [KeyValueItem(Code(b.id), b.reason) for b in bans]
    else:
        count: int = await db.banlist.total_count()
        query_results = [KeyValueItem(Bold('Total Count'), Code(count))]
    return KanTeXDocument(Section('Query Results', *query_results))


@banlist.subcommand()
async def import_(client: Client, db: Database, msg: Message) -> KanTeXDocument:
    """Import a CSV to the banlist.

    The CSV file should end in .csv and have a `id` and `reason` column

    Examples:
        {cmd}
    """
    if msg.is_reply:  # pylint: disable = R1702
        reply_msg: Message = await msg.get_reply_message()
        if reply_msg.document:
            _, ext = os.path.splitext(reply_msg.document.attributes[0].file_name)
            if ext == '.csv':
                data = await reply_msg.download_media(bytes)
                start_time = time.time()
                _banlist = await helpers.rose_csv_to_dict(data)
                if _banlist:
                    await db.banlist.upsert_multiple(_banlist)
                    if client.sw and client.sw.permission in [Permission.Admin, Permission.Root]:
                        bans = {}
                        for b in _banlist:
                            bans[b['reason']] = bans.get(b['reason'], []) + [b['id']]
                        admin_id = (await client.get_me()).id
                        for reason, uids in bans.items():
                            uids_copy = uids[:]
                            while uids_copy:
                                client.sw.add_bans([Ban(int(uid), reason, admin_id)
                                                    for uid in uids_copy[:SWAPI_SLICE_LENGTH]])
                                uids_copy = uids_copy[SWAPI_SLICE_LENGTH:]

                stop_time = time.time() - start_time
                return KanTeXDocument(Section('Import Result',
                                              f'Added {len(_banlist)} entries.'),
                                      Italic(f'Took {stop_time:.02f}s'))
            else:
                raise Error('File is not a CSV')
        else:
            raise Error('Need to reply to a document')


@banlist.subcommand()
async def importjustasic_(client: Client, db: Database, msg: Message, chat: Channel, args, kwargs) -> KanTeXDocument:
    """Import a CSV to the banlist.

    Made to import a fuckming printed python list


    who even does this

    Examples:
        {cmd}
    """
    reasontoban = kwargs.get('reason')
    if msg.is_reply:  # pylint: disable = R1702
        reply_msg: Message = await msg.get_reply_message()
        if reply_msg.document:
            _, ext = os.path.splitext(reply_msg.document.attributes[0].file_name)
            if ext == '.txt':
                data = await reply_msg.download_media(bytes)
                start_time = time.time()
                _banlist = await helpers.id_csv_to_dict(data)
                if _banlist:

                    progress_message: Message = await client.send_message(chat, f"Processing {len(_banlist)} User IDs")
                    while _banlist:
                        uid_batch = _banlist[:CHUNK_SIZE]
                        for uid in uid_batch:
                            banned, reason = await client.ungban(uid)

                        _banlist = _banlist[CHUNK_SIZE:]
                        if _banlist:
                            if progress_message:
                                await progress_message.edit(
                                    f"Sleeping for 10 seconds after banning {len(uid_batch)} Users. {len(_banlist)} Users left.")
                            await asyncio.sleep(10)

                stop_time = time.time() - start_time
                return KanTeXDocument(Section('Import Result',
                                              f'Added {len(_banlist)} entries.'),
                                      Italic(f'Took {stop_time:.02f}s'))
            else:
                raise Error('File is not a txxxt')
        else:
            raise Error('Need to reply to a document')


@banlist.subcommand()
async def export(client: Client, db: Database, chat, msg, kwargs) -> None:
    """Export the banlist as CSV.

    The format is `id,reason` and can be imported into most bots.

    Examples:
        {cmd}
    """
    start_time = time.time()
    with_diff = kwargs.get('diff', False)

    if with_diff and msg.is_reply:  # pylint: disable = R1702
        reply_msg: Message = await msg.get_reply_message()
        _, ext = os.path.splitext(reply_msg.document.attributes[0].file_name)
        if ext == '.csv':
            data = await reply_msg.download_media(bytes)
            _banlist = await helpers.rose_csv_to_dict(data)
            _banlist = [u['id'] for u in _banlist]
    else:
        _banlist = None

    if with_diff:
        users = await db.banlist.get_all_not_in(_banlist)
    else:
        users = await db.banlist.get_all()
    export = BytesIO()
    wrapper_file = codecs.getwriter('utf-8')(export)
    cwriter = csv.writer(wrapper_file, lineterminator='\n')
    cwriter.writerow(['id', 'reason'])
    for user in users:
        cwriter.writerow([user.id, user.reason])
    stop_time = time.time() - start_time
    await client.send_file(chat, export.getvalue(),
                           attributes=[DocumentAttributeFilename('banlist_export.csv')],
                           caption=str(Italic(f'Took {stop_time:.02f}s')))
