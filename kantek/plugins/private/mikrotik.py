from datetime import timedelta
from pprint import pformat
from socket import create_connection, error as SOCKET_ERROR, timeout as SOCKET_TIMEOUT
from typing import List, Dict, Tuple
import routeros

from kantex.md import *
from routeros import API, TrapError, FatalError, Socket, RouterOS
from telethon.tl.custom import Message
from telethon.tl.functions.messages import MigrateChatRequest

from database.database import Database
from utils import parsers
from utils.client import Client
from utils.parsers import MissingExpression
from utils.pluginmgr import k, _Command, _Signature

class BetterRouter():
    def create_transport(host, port):
        """
        Create a connection with host and return a open Socket
        :param host: Hostname to connect to. May be ipv4,ipv6, FQDN.
        :param port: Destination port to be used.
        :return: Socket.
        """
        try:
            sock = create_connection(address=(host, port), timeout=10)
        except (SOCKET_ERROR, SOCKET_TIMEOUT) as error:
            raise ConnectionError(error)
        return Socket(sock=sock)

    def login(username: str, password, host, port=8728, use_old_login_method=False):
        """
        Connect and login to routeros device.
        Upon success return a RouterOS class.

        :param username: Username to login with.
        :param password: Password to login with. Only ASCII characters allowed.
        :param host: Hostname to connect to. May be ipv4,ipv6, FQDN.
        :param port: Destination port to be used. Defaults to 8728.
        """
        transport = BetterRouter.create_transport(host, port)
        protocol = API(transport=transport, encoding='ASCII')
        routeros = BetterRouterOS(protocol=protocol)

        try:
            if use_old_login_method:  # Login method pre-v6.43
                sentence = routeros('/login')
                token = sentence[0]['ret']
                encoded = routeros.encode_password(token, password)
                routeros('/login', **{'name': username, 'response': encoded})
            else:  # Login method post-v6.43
                routeros('/login', **{'name': username, 'password': password})
        except (ConnectionError, TrapError, FatalError):
            transport.close()
            raise

        return routeros


class BetterRouterOS(RouterOS):
    def __call__(self, command, *args, **kwargs):
        """
        Call Api with given command.

        :param command: Command word. eg. /ip/address/print
        :param args: List with optional arguments, most used for query commands.
        :param kwargs: Dictionary with optional arguments.
        """
        if kwargs:
            args = tuple(self.compose_word(key.replace('_','-'), value) for key, value in kwargs.items())

        self.protocol.write_sentence(command, *args)
        return self._read_response()


@k.command('mikrotik', document=False)
async def mikrotik() -> None:
    """Random convenience functions for the bot developers.

    These are unsupported. Don't try to get support for them.
    """
    pass


@mikrotik.subcommand()
async def get_addr(client: Client, args, kwargs) -> KanTeXDocument:
    router = routeros.login('root', 'root', '192.168.10.1')
    res = router('/ip/address/print')

    sec = Section('Addressen')
    for i in res:
        sec.append(KeyValueItem(i['interface'], Code(i['address'])))

    return KanTeXDocument(sec)


@mikrotik.subcommand()
async def get_route(client: Client, args, kwargs) -> KanTeXDocument:
    router = routeros.login('root', 'root', '192.168.10.1')
    res = router('/ip/route/print')

    sec = Section('Routen')
    for i in res:
        sec.append(KeyValueItem(i['dst-address'], Code(i['gateway-status'].replace('reachable', ''))))

    return KanTeXDocument(sec)


@mikrotik.subcommand()
async def firewall(client: Client, args, kwargs) -> KanTeXDocument:
    # noinspection PyCallByClass
    router = BetterRouter.login('root', 'root', '192.168.10.1')



    res = router('/ip/firewall/filter/add', action=args[0], protocol=args[1], chain='forward', src_address=args[2])




    sec = Section('OK')

    sec.append(KeyValueItem('Returncode', Code(res)))
    return KanTeXDocument(sec)
