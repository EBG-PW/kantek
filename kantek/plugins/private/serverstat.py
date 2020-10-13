""""Plugin to get the fbans of the most important feds of a User."""
import logging
from typing import Dict, List, Optional

import aiohttp
from kantex.md import *
from telethon.tl.custom import Message
from telethon.tl.types import Channel

from utils.client import Client
from utils.pluginmgr import k
from utils.tags import Tags

__version__ = '0.1.2'

tlog = logging.getLogger('kantek-channel-log')


async def roundToBits(Input: int, bit) -> str:
    size = Input
    hrSize = ""
    b = size
    k = size / 1024.0
    m = size / 1048576.0
    g = size / 1073741824.0
    t = size / 1099511627776.0

    if b > 1:
        hrSize = f'{round(b, 2)}' 'bit/s' if bit else 'B'
    if k > 1:
        hrSize = f'{round(k, 2)}' 'kbit/s' if bit else 'KB'
    if m > 1:
        hrSize = f'{round(m, 2)}' 'mbit/s' if bit else 'MB'
    if g > 1:
        hrSize = f'{round(g, 2)}' 'gbit/s' if bit else 'GB'
    if t > 1:
        hrSize = f'{round(t, 2)}' 'tbit/s' if bit else 'TB'

    return hrSize



@k.command('servers', 'svs')
async def bbservers(msg: Message, tags: Tags, client: Client, db,
                    args: List, kwargs: Dict) -> Optional[KanTeXDocument]:
    """Display EBG Stats.

    This will ask the EBG API and display current server stats

    {cmd}servers
    {cmd}servers -all
    {cmd}svs
    {cmd}svs

    """
    all_true: bool = kwargs.get('all', False)



    chat: Channel = msg.chat

    if all_true:
        api_url = "https://api.ebg.pw/api/v1/serverstatus/now?all=true"

    else:
        api_url = "https://api.ebg.pw/api/v1/serverstatus/now"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            r = await resp.json()

        if resp.status == 200:

            message: KanTeXDocument = KanTeXDocument(Section(
                'All Servers:' if all_true else 'Servers:',
                SubSection(
                    'Status:',
                    KeyValueItem('Online', Code(str(r["Out"]["online"]))),
                    KeyValueItem('Offline', Code(str(r["Out"]["offline"])))
                ),

                SubSection(
                    'Total:',
                    KeyValueItem(
                        'CPU Usage',
                        Code(str(
                            round(float(r["Out"]["hardware"]["CPUused"]) / int(r["Out"]["hardware"]["CPUtotal"]) * 100,
                                  2)) + '% out of 100%')
                    ),
                    KeyValueItem(
                        'RAM Usage',
                        Code(str(
                            round(int(r["Out"]["hardware"]["RAMused"]) / int(r["Out"]["hardware"]["RAMtotal"]) * 100,
                                  2)) + '% out of ' + str(
                            await roundToBits(int(r["Out"]["hardware"]["RAMtotal"] * 1024), False)))
                    ),
                    KeyValueItem(
                        'DISK Usage',
                        Code(str(
                            round(int(r["Out"]["hardware"]["DISKused"]) / int(r["Out"]["hardware"]["DISKtotal"]) * 100,
                                  2)) + '% out of ' + str(
                            await roundToBits(int(r["Out"]["hardware"]["DISKtotal"] * 1024 * 1024), False)))
                    ),
                    KeyValueItem(
                        'Traffic',
                        f'D↓: {Code(await roundToBits(int(r["Out"]["hardware"]["NETrx"]), True))} /'
                        f' U↑: {Code(await roundToBits(int(r["Out"]["hardware"]["NETtx"]), True))} '
                    )
                ),
            ))

            if len(r["Out"]["offlineservers"]) > 0:
                offline_servers: Section = Section('Offline Devices:')
                for i in r["Out"]["offlineservers"]:
                    offline_servers.append(KeyValueItem(
                        i["name"], f'{Code(i["type"])} ({Code(i["location"])})',
                    ))
                message.append(offline_servers)
            await session.close()
            return message

        else:
            await session.close()
            print("Failed")
            return KanTeXDocument(Section('Error', SubSection(Code('There was an error with the API'))))
