import asyncio, os, json, time
import views.mainwindow as main_window
import models.bot_commands as bot_commands
import models.bot_client_handler as bot_client_handler


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
  "bot_commands": dict[str, type[dict]],
  "bot_keywords": dict[str, type[str]]
}
_loop = asyncio.new_event_loop()


def execute_thread():
  global settings, logged

  with open(os.path.join(os.getcwd(), "settings.json"), "r", encoding="utf8") as file:
    settings = json.load(file)
  
  main_window.add_to_chat("Awaiting connection...")
  bot_client_handler.login()

  for _ in range(100):
    if bot_client_handler._tmi_client.logged: break
    else: time.sleep(0.1)
  if not bot_client_handler._tmi_client.logged: raise ConnectionError("Cannot connect! Try to restart the bot.")
  logged = True
  main_window.add_to_chat("Connected !")

  for channel in settings['bot_settings']['auto_join']:
    join_channel(channel, auto=True)
    _handle_buffer()
  
  time.sleep(1) # TO BE SURE THE TABS ARE OPENED ON MAINWINDOW
  
  while True:
    _handle_buffer()
    if main_window.window_closed:
      for channel in main_window.get_channels(): _loop.run_until_complete(bot_client_handler.part(channel))
      bot_client_handler.logout()
      break
    time.sleep(0.1)


def join_channel(channel: str, auto=False):
  channel = str("#"+channel).lower() if channel[0] != "#" else channel.lower()
  main_window.add_to_chat(f"{'[Auto-Join] ' if auto else ''}Joining {channel}...")
  _loop.run_until_complete(bot_client_handler.send_message(channel, settings['bot_settings']['welcome_message']))
  _loop.run_until_complete(bot_client_handler.join(channel))
  main_window.add_tab(channel)
  main_window.add_to_chat(f"Joined {channel} !")


def leave_channel(channel: str):
  main_window.add_to_chat(f"Leaving {channel}...")
  _loop.run_until_complete(bot_client_handler.send_message(channel, settings['bot_settings']['part_message']))
  _loop.run_until_complete(bot_client_handler.part(channel))
  for buffer_message in bot_client_handler.history_buffer:
    if isinstance(buffer_message, list) and buffer_message[1] == channel: bot_client_handler.history_buffer.remove(buffer_message)
  main_window.remove_tab(channel)
  main_window.add_to_chat(f"Leaved {channel} !")


def send_to_channel(channel: str, message: str):
  _loop.run_until_complete(bot_client_handler.send_message(channel, message))
  main_window.add_to_chat(f"[BOT][{channel}]: {message}", channel)


def _handle_buffer():
  while bot_client_handler.history_buffer != []:
    try:
      if isinstance(bot_client_handler.history_buffer[0], list):
        user, channel, message = bot_client_handler.history_buffer[0]
        if message.startswith(settings['bot_settings']['command_prefix']): bot_commands.handle_command(user, channel, message[1:])
        if settings['bot_settings']['debug']: main_window.add_to_chat(f"[DEBUG] {user}: {message}", channel)
      elif isinstance(bot_client_handler.history_buffer[0], str):
        message = bot_client_handler.history_buffer[0]
        if settings['bot_settings']['debug']: main_window.add_to_chat(f"[DEBUG] {message}")
      bot_client_handler.history_buffer.remove(bot_client_handler.history_buffer[0])
    except IndexError: pass
