import asyncio, pytmi, threading
import models.shared_data as shared


TRACE_MODE = True  ### FOR DEBUG ###


class ClientThread():
  tmi_client: pytmi.TmiClient

  def __init__(self):
    self.tmi_client = pytmi.TmiClient(ssl=False)
    self.loop = asyncio.new_event_loop()
    self._thread = threading.Thread(name="ClientThread", target=self.loop.run_forever)
    self._thread.daemon = True
    self._thread.start()

  def login(self):
    asyncio.run_coroutine_threadsafe(self.tmi_client.login_oauth(token=shared.credentials['token'], nick=shared.credentials['nick'], retry=10), self.loop)
    asyncio.run_coroutine_threadsafe(self._init(), self.loop)
  
  def logout(self):
    self._cancel_listen()
    asyncio.run_coroutine_threadsafe(self.tmi_client.logout(), self.loop)

  async def join(self, channel: str):
    self._cancel_listen()
    await self.tmi_client.join(channel)
    asyncio.run_coroutine_threadsafe(self._init(), self.loop)

  async def part(self, channel: str):
    self._cancel_listen()
    await self.tmi_client.part(channel)
    asyncio.run_coroutine_threadsafe(self._init(), self.loop)

  async def send_message(self, channel: str, text: str):
    self._cancel_listen()
    await self.tmi_client.send_privmsg(text, channel)
    asyncio.run_coroutine_threadsafe(self._init(), self.loop)
  
  async def _init(self):
    async def _listen():
      while True:
        try: raw = await self.tmi_client.get_privmsg()
        except: break
        msg = pytmi.TmiMessage(raw)
        if msg.command.split(" ")[0] == "PRIVMSG":
          user_channel = msg.command[msg.command.find("#"):msg.command.find(" ", msg.command.find("#"))]
          user_message = msg.command[(msg.command.find(":") + 1):]
          shared.history_buffer.append([msg.tags['display-name'], user_channel, user_message])
        elif msg.command.split(" ")[0] == "JOIN" or msg.command.split(" ")[0] == "PART" and TRACE_MODE:
          user = msg.raw[1:msg.raw.find("!")]
          shared.history_buffer.append(f"[TRACE] {user} {msg.command}")
        elif TRACE_MODE: shared.history_buffer.append(f"[TRACE] {msg.command}")

    self.listen_task = self.loop.create_task(_listen())

  def _cancel_listen(self):
    try: self.loop.call_soon_threadsafe(self.listen_task.cancel)
    except: pass
