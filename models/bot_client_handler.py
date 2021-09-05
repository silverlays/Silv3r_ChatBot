import asyncio, pytmi, threading
from typing import Union


TRACE_MODE = False  ### FOR DEBUG ###

credentials: dict[str, type[str]]
history_buffer: Union[list[str], list[list[str, str, str]]] = []
tmi_client: pytmi.TmiClient
listen_task: asyncio.Task[type[asyncio.create_task]]
tmi_client = pytmi.TmiClient(ssl=False)
loop = asyncio.new_event_loop()
_thread = threading.Thread(name="ClientThread", target=loop.run_forever)
_thread.daemon = True
_thread.start()


def login():
  asyncio.run_coroutine_threadsafe(tmi_client.login_oauth(token=credentials['token'], nick=credentials['nick'], retry=10), loop)
  asyncio.run_coroutine_threadsafe(_init(), loop)


def logout():
  _cancel_listen()
  asyncio.run_coroutine_threadsafe(tmi_client.logout(), loop)


async def join(channel: str):
  _cancel_listen()
  await tmi_client.join(channel)
  asyncio.run_coroutine_threadsafe(_init(), loop)


async def part(channel: str):
  _cancel_listen()
  await tmi_client.part(channel)
  asyncio.run_coroutine_threadsafe(_init(), loop)


async def send_message(channel: str, text: str):
  _cancel_listen()
  await tmi_client.send_privmsg(text, channel)
  asyncio.run_coroutine_threadsafe(_init(), loop)


async def _init():
  async def _listen():
    while True:
      try: raw = await tmi_client.get_privmsg()
      except: break
      msg = pytmi.TmiMessage(raw)
      if msg.command.split(" ")[0] == "PRIVMSG":
        user_channel = msg.command[msg.command.find("#"):msg.command.find(" ", msg.command.find("#"))]
        user_message = msg.command[(msg.command.find(":") + 1):]
        history_buffer.append([msg.tags['display-name'], user_channel, user_message])
      elif msg.command.split(" ")[0] == "JOIN" or msg.command.split(" ")[0] == "PART" and TRACE_MODE:
        user = msg.raw[1:msg.raw.find("!")]
        print(f"[TRACE] {user} {msg.command}")
      elif TRACE_MODE: print(f"[TRACE] {msg.command}")
  listen_task = loop.create_task(_listen())


def _cancel_listen():
  try: loop.call_soon_threadsafe(listen_task.cancel)
  except: pass
