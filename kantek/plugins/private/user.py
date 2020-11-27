import logging
from typing import Union, Dict, List, Optional

from kantex.md import *
from spamwatch.client import Client as SWOClient
from spamwatch.types import Permission
from telethon.tl.custom import Forward, Message
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMention, MessageEntityMentionName, User, Channel, UserFull

import utils.errors
from database.database import Database
from utils import helpers, constants
from utils.client import Client
from utils.config import Config
from utils.pluginmgr import k
from utils.tags import Tags

tlog = logging.getLogger('kantek-channel-log')


@k.command('user', 'u')
async def user_info(msg: Message, tags: Tags, client: Client, db: Database,
                    args: List, kwargs: Dict) -> Optional[KanTeXDocument]:
    """Show information about a user. Can be used in reply to a message.

    Arguments:
        `ids`: List of User IDs
        `-mention`: Mention the user
        `-id`: Output information in a `name: id` format
        `-full`: Output the full message a user was banned for
        `-gban`: Output user ids space seperated for `{prefix}gban`
        `-all`: Enable all of the flags below
        `-general`: General info, enabled by default
        `-bot`: Output bot specific information
        `-misc`: Output miscellaneous information
        `-ng`: Exclude general information
        `-ebg`: Output all information from the EBG-Watch API
        `-sw`: Output all information from the SpamWatch API
        `-bw`: Output all information from the BolverWatch API
        `-spb`: Show information from SpamProtectionBot
        `-spe`: Output Analysis vor suspicius Activity and cuteness
        `c`: Optionaly specify cuteness based on manual review

    Tags:
        strafanzeige:
            True: Append a short value to autofill user id and message link for {prefix}gban

    Examples:
        {cmd} 777000
        {cmd} 777000 -mention
        {cmd} 777000 -mention -id
        {cmd} @username
        {cmd} 777000 -all
        {cmd} 777000 -sw
        {cmd} -sa
    """
    if not args and msg.is_reply:
        return await _info_from_reply(client, msg, db, kwargs, tags)
    elif args:
        return await _info_from_arguments(client, msg, db, args, kwargs)


async def _info_from_arguments(client, msg, db, args, kwargs) -> KanTeXDocument:
    gban_format = kwargs.get('gban', False)
    entities = []
    for entity in msg.get_entities_text():
        obj, text = entity
        if isinstance(obj, MessageEntityMentionName):
            entities.append(obj.user_id)
        elif isinstance(obj, MessageEntityMention):
            entities.append(text)
    # append any user ids to the list
    for uid in args:
        if isinstance(uid, int):
            entities.append(uid)

    users = []
    errors = []
    for entity in entities:
        try:
            user: User = await client.get_entity(entity)
            try:
                full = await client(GetFullUserRequest(entity))

            except:
                full = None
                pass
            if isinstance(user, Channel):
                errors.append(str(entity))
                continue
            users.append(str(await _collect_user_info(client, user, db, full=full, **kwargs)))
        except constants.GET_ENTITY_ERRORS:
            errors.append(str(entity))
    if users and gban_format:
        users = [Code(' '.join(users))]
    if users or errors:
        return KanTeXDocument(*users, (Section('Errors for', Code(', '.join(errors)))) if errors else '')


async def _info_from_reply(client, msg, db, kwargs, tags) -> KanTeXDocument:
    get_forward = kwargs.get('forward', True)
    anzeige = tags.get('strafanzeige', True) or kwargs.get('sa', False)

    reply_msg: Message = await msg.get_reply_message()

    if get_forward and reply_msg.forward is not None:
        forward: Forward = reply_msg.forward
        if forward.sender_id is None:
            raise utils.errors.Error('User has forward privacy enabled')
        user: User = await client.get_entity(forward.sender_id)
    else:
        user: UserFull = await client.get_entity(reply_msg.sender_id)

    user_section = await _collect_user_info(client, user, db, **kwargs)
    if anzeige and isinstance(user_section, Section):
        data = await helpers.create_strafanzeige(user.id, reply_msg)
        key = await db.strafanzeigen.add(data)
        user_section.append(SubSection('Strafanzeige', KeyValueItem('code', Code(f'sa: {key}'))))
    return KanTeXDocument(user_section)


async def _collect_user_info(client, user, db, **kwargs) -> Union[str, Section, KeyValueItem]:
    id_only = kwargs.get('id', False)
    gban_format = kwargs.get('gban', False)
    show_general = kwargs.get('general', True)
    show_bot = kwargs.get('bot', False)
    show_misc = kwargs.get('misc', False)
    show_spe = kwargs.get('spe', False)
    show_all = kwargs.get('all', False)
    full_ban_msg = kwargs.get('full', False)
    show_ebgwatch = kwargs.get('ebg', False)
    show_spamwatch = kwargs.get('sw', False)
    show_bolverwatch = kwargs.get('bw', False)
    show_spb = kwargs.get('spb', False)
    is_cute = kwargs.get('c', False)
    full = kwargs.get('full')

    if kwargs.get('ng', False):
        show_general = False

    config = Config()
    if config.original_spamwatch_token:
        swoclient = SWOClient(config.original_spamwatch_token)
    if config.bolver_spamwatch_token:
        try:

            swbclient = SWOClient(config.bolver_spamwatch_token, host='https://spamapi.bolverblitz.net/')
        except:
            swbclient = None

    else:
        swbclient = None

    if show_all:
        show_general = True
        show_bot = True
        show_misc = True
        show_spamwatch = True
        show_spe = True
        show_ebgwatch = True
        show_bolverwatch = True
        show_spb = True

    mention_name = kwargs.get('mention', False)

    full_name = await helpers.get_full_name(user)
    if mention_name:
        title = Link(full_name, f'tg://user?id={user.id}')
    else:
        title = Bold(full_name)

    ebg_ban = None
    sw_ban = None
    ban_reason = await db.banlist.get(user.id)
    if ban_reason:
        ban_reason = ban_reason.reason
    if client.sw and client.sw.permission.value <= Permission.User.value:
        ebg_ban = client.sw.get_ban(int(user.id))
        if ebg_ban:
            ebg_ban_message = ebg_ban.message
            if ebg_ban_message and not full_ban_msg:
                ebg_ban_message = f'{ebg_ban_message[:128]}{"[...]" if len(ebg_ban_message) > 128 else ""}'

    if swoclient and swoclient.permission.value <= Permission.User.value:
        sw_ban = swoclient.get_ban(int(user.id))
        if sw_ban:
            sw_ban_message = sw_ban.message
            if sw_ban_message and not full_ban_msg:
                sw_ban_message = f'{sw_ban_message[:128]}{"[...]" if len(sw_ban_message) > 128 else ""}'

    if swbclient is not None:
        if swbclient and swbclient.permission.value <= Permission.User.value:
            bw_ban = swbclient.get_ban(int(user.id))
            if bw_ban:
                bw_ban_message = bw_ban.message
                if bw_ban_message and not full_ban_msg:
                    bw_ban_message = f'{bw_ban_message[:128]}{"[...]" if len(bw_ban_message) > 128 else ""}'

    if show_spb:
        params = {'query': user.id}
        async with client.aioclient.get(f'https://api.intellivoid.net/spamprotection/v1/lookup', params=params) as response:

            spb_info = await response.json()


    if id_only:
        return KeyValueItem(title, Code(user.id))
    elif gban_format:
        return str(user.id)
    else:
        general = SubSection(
            Bold('General'),
            KeyValueItem('id', Code(user.id)),
            KeyValueItem('first_name', Code(user.first_name)))
        if user.last_name is not None or show_all:
            general.append(KeyValueItem('last_name', Code(user.last_name)))
        if user.username is not None or show_all:
            general.append(KeyValueItem('username', Code(user.username)))

        if user.scam or show_all:
            general.append(KeyValueItem('scam', Code(user.scam)))

        if ban_reason:
            general.append(KeyValueItem('ban_reason', Code(ban_reason)))
        elif not ebg_ban:
            general.append(KeyValueItem('gbanned', Code('False')))
        if ebg_ban and not show_ebgwatch:
            general.append(KeyValueItem('ban_msg', Code(ebg_ban_message)))

        ebgwatch = SubSection('EBGWatch')
        if ebg_ban:
            ebgwatch.extend([
                KeyValueItem('reason', Code(ebg_ban.reason)),
                KeyValueItem('date', Code(ebg_ban.date)),
                KeyValueItem('timestamp', Code(ebg_ban.timestamp)),
                KeyValueItem('admin', Code(ebg_ban.admin)),
                KeyValueItem('message', Code(ebg_ban_message)),
            ])
        elif not client.sw:
            ebgwatch.append(Italic('Disabled'))
        else:
            ebgwatch.append(KeyValueItem('banned', Code('False')))

        spamwatch = SubSection('SpamWatch')
        if sw_ban:
            spamwatch.extend([
                KeyValueItem('reason', Code(sw_ban.reason)),
                KeyValueItem('date', Code(sw_ban.date)),
                KeyValueItem('timestamp', Code(sw_ban.timestamp)),
                KeyValueItem('admin', Code(sw_ban.admin)),
                KeyValueItem('message', Code(sw_ban_message)),
            ])
        elif not swoclient:
            spamwatch.append(Italic('Disabled'))
        else:
            spamwatch.append(KeyValueItem('banned', Code('False')))

        bolverwatch = SubSection('BolverWatch')
        if swbclient is not None:
            if bw_ban:
                bolverwatch.extend([
                    KeyValueItem('reason', Code(bw_ban.reason)),
                    KeyValueItem('date', Code(bw_ban.date)),
                    KeyValueItem('timestamp', Code(bw_ban.timestamp)),
                    KeyValueItem('admin', Code(bw_ban.admin)),
                    KeyValueItem('message', Code(bw_ban_message)),
                ])
            elif not swbclient:
                bolverwatch.append(Italic('Disabled'))
            else:
                bolverwatch.append(KeyValueItem('banned', Code('False')))
        else:
            bolverwatch.append(Italic('Disabled'))
        spb_section = SubSection('SpamProtection')
        if show_spb:
            if spb_info['success']:
                spb_section.extend([
                        KeyValueItem('PTGid', Code(spb_info['results']['private_telegram_id'])),
                        KeyValueItem('lang', Code(spb_info['results']['language_prediction']['language'])),
                        KeyValueItem('spam/ham', KeyValueItem(Code(spb_info['results']['spam_prediction']['spam_prediction']), Code(spb_info['results']['spam_prediction']['ham_prediction']))),


                ])
                if spb_info['results']['attributes']['is_blacklisted']:
                    spb_section.extend([
                        KeyValueItem('reason', Code(spb_info['results']['attributes']['blacklist_reason'])),
                        KeyValueItem('pot-spam', Code(spb_info['results']['attributes']['is_potential_spammer'])),
                        KeyValueItem('flag', Code(spb_info['results']['attributes']['blacklist_flag'])),

                    ])

                else:
                    spb_section.append(KeyValueItem('banned', Code('False')))
            else:
                spb_section.append(KeyValueItem('Error', Code(spb_info['error']['message'])))




        bot = SubSection(
            Bold('Bot'),
            KeyValueItem('bot', Code(user.bot)),
            KeyValueItem('bot_chat_history', Code(user.bot_chat_history)),
            KeyValueItem('bot_info', Code(full.bot_info if hasattr(full, 'bot_info') else None)),
            KeyValueItem('bot_info_version', Code(user.bot_info_version)),
            KeyValueItem('bot_inline_geo', Code(user.bot_inline_geo)),
            KeyValueItem('bot_inline_placeholder',
                         Code(user.bot_inline_placeholder)),
            KeyValueItem('bot_nochats', Code(user.bot_nochats)))
        misc = SubSection(
            Bold('Misc'),
            KeyValueItem('mutual_contact', Code(user.mutual_contact)),
            KeyValueItem('restricted', Code(user.restricted)),
            KeyValueItem('restriction_reason', Code(user.restriction_reason)),
            KeyValueItem('deleted', Code(user.deleted)),
            KeyValueItem('verified', Code(user.verified)),
            KeyValueItem('min', Code(user.min)),
            KeyValueItem('lang_code', Code(user.lang_code)))

        special_stuff = SubSection('Additional Info')
        if show_spe:

            cute: str = ('yes' if (user.id == 483808054) else 'no' )
            if is_cute:
                cute: str = f'{user.first_name} is {is_cute}'
            sus: str = ('yes' if ((user.id % 2) == 0) and (user.id > 100000000) else 'no')

            special_stuff.extend([
                KeyValueItem('Cute', cute),
                KeyValueItem('Sus', sus)
             ])

        return Section(title,
                       general if show_general else None,
                       ebgwatch if show_ebgwatch else None,
                       spamwatch if show_spamwatch else None,
                       bolverwatch if show_bolverwatch else None,
                       spb_section if show_spb else None,
                       misc if show_misc else None,
                       special_stuff if show_spe else None,
                       bot if show_bot else None)
