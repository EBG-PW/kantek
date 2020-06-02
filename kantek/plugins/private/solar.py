"""Plugin to log every event because yolo"""
import logging
from typing import Dict

import logzero
import requests
from telethon import events

__version__ = '0.4.1'

from telethon.events import NewMessage

from database.arango import ArangoDB
from utils.client import KantekClient
from utils.mdtex import MDTeXDocument, Section, Bold, KeyValueItem
from config import cmd_prefix

tlog = logging.getLogger('kantek-channel-log')
logger: logging.Logger = logzero.logger


@events.register(events.NewMessage(outgoing=True, pattern=f'{cmd_prefix}s(olar)s(tats)'))
async def solar(event: NewMessage.Event) -> None:
    """Plugin to send current solar statistics of owls home."""
    client: KantekClient = event.client
    db: ArangoDB = client.db
    chat_document = db.groups.get_chat(event.chat_id)
    db_named_tags: Dict = chat_document['named_tags'].getStore()

    response = requests.get('http://192.168.10.180/solar_api/v1/GetInverterRealtimeData.cgi?Scope=System&DataCollection=NowSensorData')
    data = response.json()


    await client.respond(event, str(MDTeXDocument(
        Section(f"{Bold('GodOfOwls PV Unit:')}",
                KeyValueItem(Bold('Aktuell'), str(data['Body']['Data']['PAC']['Values']['1'])+str(data['Body']['Data']['PAC']['Unit'])),
                KeyValueItem(Bold('Tagesenergie'), str(data['Body']['Data']['DAY_ENERGY']['Values']['1'])+str(data['Body']['Data']['DAY_ENERGY']['Unit'])),
                KeyValueItem(Bold('Jahresenergie'), str(data['Body']['Data']['YEAR_ENERGY']['Values']['1'])+str(data['Body']['Data']['YEAR_ENERGY']['Unit'])),
                KeyValueItem(Bold('Gesamtenergie'), str(data['Body']['Data']['TOTAL_ENERGY']['Values']['1'])+str(data['Body']['Data']['TOTAL_ENERGY']['Unit']))))))
