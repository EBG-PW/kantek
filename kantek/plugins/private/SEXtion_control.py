# by my kawaii neko -> t.me/TheKneeSocks
import asyncio
import html
from typing import List, Dict, Optional

import aiohttp, json
from kantex.md import *
from telethon import events
from telethon.tl.types import Channel, Message

from database.database import Database
from utils.client import Client
from utils.pluginmgr import k, Command


from utils.tags import Tags

zws = '\u200b'

@k.command("prn")
async def wordl_lister(client: Client, db: Database, tags: Tags, chat: Channel, msg: Message,
               args: List, kwargs: Dict, event: Command) -> Optional[KanTeXDocument]:
    """Seporn pics
       Powered by nekos.life iirc

    Examples:
        8ball - Gets a picture of 8ball
        random_hentai_gif - Gets a gif of random_hentai_gif
        meow - Gets a picture of meow
        erok - Gets a picture of erok
        lizard - Gets a picture of lizard
        feetg - Gets a picture of feetg
        baka - Gets a picture of baka
        bj - Gets a picture of bj
        erokemo - Gets a picture of erokemo
        tickle - Gets a picture of tickle
        feed - Gets a picture of feed
        neko - Gets a picture of neko
        kuni - Gets a picture of kuni
        femdom - Gets a picture of femdom
        futanari - Gets a picture of futanari
        smallboobs - Gets a picture of smallboobs
        goose - Gets a picture of goose
        poke - Gets a picture of poke
        les - Gets a picture of les
        trap - Gets a picture of trap
        pat - Gets a picture of pat
        boobs - Gets a picture of boobs
        blowjob - Gets a picture of blowjob
        hentai - Gets a picture of hentai
        hololewd - Gets a picture of hololewd
        ngif - Gets a gif of ngif
        fox_girl - Gets a picture of fox_girl
        wallpaper - Gets a picture of wallpaper
        lewdk - Gets a picture of lewdk
        solog - Gets a picture of solog
        pussy - Gets a picture of pussy
        yuri - Gets a picture of yuri
        lewdkemo - Gets a picture of lewdkemo
        lewd - Gets a picture of lewd
        anal - Gets a picture of anal
        pwankg - Gets a picture of pwankg
        nsfw_avatar - Gets a picture of nsfw_avatar
        eron - Gets a picture of eron
        kiss - Gets a picture of kiss
        pussy_jpg - Gets a picture of pussy_jpg
        woof - Gets a picture of woof
        hug - Gets a picture of hug
        keta - Gets a picture of keta
        cuddle - Gets a picture of cuddle
        eroyuri - Gets a picture of eroyuri
        slap - Gets a picture of slap
        cum_jpg - Gets a picture of cum_jpg
        waifu - Gets a picture of waifu
        gecg - Gets a picture of gecg
        tits - Gets a picture of tits
        avatar - Gets a picture of avatar
        holoero - Gets a picture of holoero
        classic - Gets a picture of classic
        kemonomimi - Gets a picture of kemonomimi
        feet - Gets a picture of feet
        gasm - Gets a picture of gasm
        spank - Gets a picture of spank
        erofeet - Gets a picture of erofeet
        ero - Gets a picture of ero
        solo - Gets a picture of solo
        cum - Gets a picture of cum
        smug - Gets a picture of smug
        holo - Gets a picture of holo
        nsfw_neko_gif - Gets a gif of nsfw_neko_gif
    """

    async with aiohttp.ClientSession() as session:
            async with session.get(f'https://nekos.life/api/v2/img/{args[0]}') as resp:
                print(resp.status)
                data = await resp.json()


    await client.respond(event, str(data['url']), link_preview=True)

