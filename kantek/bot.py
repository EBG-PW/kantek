"""Main bot module. Setup logging, register components"""
import asyncio
import logging

import logzero
from spamwatch.client import Client as SWClient

from database.database import Database
from utils import helpers
from utils.client import Client
from utils.config import Config
from utils.loghandler import TGChannelLogHandler
from utils.pluginmgr import PluginManager

import resource
resource.setrlimit(resource.RLIMIT_AS, (2147483648, 2147483648))

logger = logzero.setup_logger('kantek-logger', level=logging.DEBUG)
telethon_logger = logzero.setup_logger('telethon', level=logging.DEBUG, logfile='log.log')

tlog = logging.getLogger('kantek-channel-log')

tlog.setLevel(logging.INFO)

__version__ = '0.3.1'


async def main() -> None:
    """Register logger and components."""
    config = Config()

    handler = TGChannelLogHandler(config.log_bot_token,
                                  '-1001418023497')
    await handler.connect()
    tlog.addHandler(handler)

    db = Database()
    await db.connect(config)

    client = Client(str(config.session_name), config.api_id, config.api_hash, request_retries=8, retry_delay=10, auto_reconnect=True, flood_sleep_threshold=60)
    # noinspection PyTypeChecker

    await client.connect()
    if not await client.is_user_authorized():
        await client.start()
    client.config = config
    client.kantek_version = __version__

    client.plugin_mgr = PluginManager(client)
    client.plugin_mgr.register_all()

    logger.info('Connecting to Database')
    client.db = db

    tlog.info('Started Kantek v%s [%s]', __version__, helpers.link_commit(helpers.get_commit()))
    logger.info('Started Kantek v%s', __version__)

    if config.spamwatch_host and config.spamwatch_token:
        client.sw = SWClient(config.spamwatch_token, host=config.spamwatch_host)
        client.swo = SWClient(config.original_spamwatch_token)
        client.sw_url = config.spamwatch_host
    ich = await client.get_me()
    if not ich:
        client.self_id = 12345678
    else:
        client.self_id = ich.id

    await client.db.hashlist.add_column(self_id=client.self_id)
    print(config.sudos)
    #await client.catch_up()
    await client.run_until_disconnected()


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
