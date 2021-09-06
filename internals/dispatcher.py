import asyncio, os, json, time
import mainwindow
import commands_handler
import internals.tmi_handler as tmi_handler


logged = False
settings = {
  "bot_settings": {
    "debug": bool,
    "timestamp": bool,
    "command_prefix": str,
    "welcome_message": str,
    "part_message": str,
    "auto_join": list[str]
  },
  "commands_handler": dict[str, type[dict]],
  "bot_keywords": dict[str, type[str]]
}
_loop = asyncio.new_event_loop()


def execute_thread():
  global settings, logged

  with open(os.path.join(os.getcwd(), "settings.json"), "r", encoding="utf8") as file:
    settings = json.load(file)
  
  mainwindow.add_to_chat("Awaiting connection...")
  tmi_handler.login()
  for _ in range(100):
    if tmi_handler._tmi_client.logged:
      logged = True
      break
    else: time.sleep(0.1)
  if not logged:
    raise ConnectionError("Cannot connect! Try to restart the bot.")
  mainwindow.add_to_chat("Connected !")

  for channel in settings['bot_settings']['auto_join']:
    join_channel(channel, auto=True)
    _handle_buffer()
  
  time.sleep(1) # TO BE SURE THE TABS ARE OPENED ON MAINWINDOW
  
  while True:
    _handle_buffer()
    if mainwindow.window_closed:
      for channel in mainwindow.get_channels(): _loop.run_until_complete(tmi_handler.part(channel))
      tmi_handler.logout()
      break
    time.sleep(0.1)


def join_channel(channel: str, auto=False):
  channel = str("#"+channel).lower() if channel[0] != "#" else channel.lower()
  mainwindow.add_to_chat(f"{'[Auto-Join] ' if auto else ''}Joining {channel}...")
  _loop.run_until_complete(tmi_handler.send_message(channel, settings['bot_settings']['welcome_message']))
  _loop.run_until_complete(tmi_handler.join(channel))
  mainwindow.add_tab(channel)
  mainwindow.add_to_chat(f"Joined {channel} !")


def leave_channel(channel: str):
  mainwindow.add_to_chat(f"Leaving {channel}...")
  _loop.run_until_complete(tmi_handler.send_message(channel, settings['bot_settings']['part_message']))
  _loop.run_until_complete(tmi_handler.part(channel))
  for buffer_message in tmi_handler.history_buffer:
    if isinstance(buffer_message, list) and buffer_message[1] == channel: tmi_handler.history_buffer.remove(buffer_message)
  mainwindow.remove_tab(channel)
  mainwindow.add_to_chat(f"Leaved {channel} !")


def send_to_channel(channel: str, message: str):
  _loop.run_until_complete(tmi_handler.send_message(channel, message))
  mainwindow.add_to_chat(f"[BOT][{channel}]: {message}", channel)


def _handle_buffer():
  while tmi_handler.history_buffer != []:
    try:
      if isinstance(tmi_handler.history_buffer[0], list):
        user, channel, message = tmi_handler.history_buffer[0]
        if message.startswith(settings['bot_settings']['command_prefix']): commands_handler.handle_command(user, channel, message[1:])
        if settings['bot_settings']['debug']: mainwindow.add_to_chat(f"[DEBUG] {user}: {message}", channel)
      elif isinstance(tmi_handler.history_buffer[0], str):
        message = tmi_handler.history_buffer[0]
        if settings['bot_settings']['debug']: mainwindow.add_to_chat(f"[DEBUG] {message}")
      tmi_handler.history_buffer.remove(tmi_handler.history_buffer[0])
    except IndexError: pass
