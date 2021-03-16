# by my kawaii neko -> t.me/TheKneeSocks
import asyncio
import html
from jikanpy import AioJikan
from telethon import events
from utils.pluginmgr import k


zws = '\u200b'

@k.command("anime")
async def mal_anime(event):
    """Search anime from Kantek itself
       Powered by jikan.moe

    Examples:
        {cmd} command
    """
    async with AioJikan() as jikan:
        sr = await jikan.search('anime', event.text.split(" ", 1))
        a = await jikan.anime(sr['results'][0]['mal_id'])
    if not a:
        await event.reply('err \\\nNo results found')
        return
    text = f'<b>{html.escape(a["title"])}'
    if a['title_japanese']:
        text += f' ({html.escape(a["title_japanese"])})'
    text += '</b>\n'
    text += f'<b>Score:</b> {a["score"]}\n'
    text += f'<b>Type:</b> {html.escape(a["type"])}\n'
    text += f'<b>Genres:</b> {", ".join([html.escape(i["name"]) for i in a["genres"]])}\n'
    text += f'<b>Status:</b> {html.escape(a["status"])}\n'
    text += f'<b>Episodes:</b> {a["episodes"]}\n'
    text += f'<b>Duration:</b> {html.escape(a["duration"])}\n'
    text += f'<i>{html.escape(a["synopsis"])}</i>\n'
    pic = f'{a["image_url"]}'
    url = f'<a href="{html.escape(a["url"])}">read more</a>'
    text = text.strip()
    if len(text) > 1024:
        text =text[0:500] + ".... "
    text = text + url
    try:
        await event.reply(text, file=pic, link_preview=False, parse_mode='html')
    except BaseException:
        await event.reply(text, link_preview=False, parse_mode='html')

@k.command("manga")
async def mal_manga(event):
    """Search manga from Kantek itself
       Powered by jikan.moe

    Examples:
        {cmd} command
    """
    async with AioJikan() as jikan:
        sr = await jikan.search('manga', event.text.split(" ", 1))
        m = await jikan.manga(sr['results'][0]['mal_id'])
    if not m:
        await event.reply('err \\\nNo results found')
        return
    text = f'<b>{html.escape(m["title"])}'
    if m['title_japanese']:
        text += f' ({html.escape(m["title_japanese"])})'
    text += '</b>\n'
    text += f'<b>Score:</b> {m["score"]}\n'
    text += f'<b>Type:</b> {html.escape(m["type"])}\n'
    text += f'<b>Genres:</b> {", ".join([html.escape(i["name"]) for i in m["genres"]])}\n'
    text += f'<b>Status:</b> {html.escape(m["status"])}\n'
    if m['volumes']:
        text += f'<b>Volumes:</b> {m["volumes"]}\n'
    if m['chapters']:
        text += f'<b>Chapters:</b> {m["chapters"]}\n'
    text += f'<i>{html.escape(m["synopsis"])}</i>\n'
    pic = f'{m["image_url"]}'
    url = f'<a href="{html.escape(m["url"])}">read more</a>'
    text = text.strip()
    if len(text) > 1024:
        text =text[0:500] + ".... "
    text = text + url
    try:
        await event.reply(text, file=pic, link_preview=False, parse_mode='html')
    except BaseException:
        await event.reply(text, link_preview=False, parse_mode='html')

@k.command("character")
async def mal_character(event):
    """Search anime characters from Kantek itself
       Powered by jikan.moe

    Examples:
        {cmd} command
    """
    async with AioJikan() as jikan:
        sr = await jikan.search('character', event.text.split(" ", 1))
        c = await jikan.character(sr['results'][0]['mal_id'])
    if not c:
        await event.reply('err \\\nNo results found')
        return
    text = f'<b>{html.escape(c["name"])}'
    if c['name_kanji']:
        text += f' ({html.escape(c["name_kanji"])})'
    text += '</b>\n'
    about = html.escape(c['about'].replace('\\n', ''))
    text += f'<i>{about}</i>\n'
    pic = f'{c["image_url"]}'
    url = f'<a href="{html.escape(c["url"])}">read more</a>'
    text = text.strip()
    if len(text) > 1024:
        text =text[0:500] + ".... "
    text = text + url
    try:
        await event.reply(text, file=pic, link_preview=False, parse_mode='html')
    except BaseException:
        await event.reply(text, link_preview=False, parse_mode='html')
