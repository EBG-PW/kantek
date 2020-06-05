"""Plugin to stalk peoples"""
import logging
import socket
from typing import Union

import logzero
from telethon import events
from telethon.events import ChatAction, NewMessage

from config2 import esp_ip, esp_port

logger: logging.Logger = logzero.logger


@events.register(events.chataction.ChatAction())
@events.register(events.NewMessage())
async def blinky(event: Union[ChatAction.Event, NewMessage.Event]) -> None:
    byte_message = bytes("eule", "utf-8")
    opened_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = esp_ip
    port = esp_port
    opened_socket.sendto(byte_message, (ip, port))
