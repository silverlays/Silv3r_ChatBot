import asyncio, os, json, time
import models.shared_data as shared
from PySimpleGUI import Multiline
from models.client_thread import ClientThread


SETTINGS_FILE = os.path.join(os.getcwd(), "settings.json")


class BotThread():
  def __init__(self):
    shared.client_thread = ClientThread()

  def execute_thread(self):
    self.loop = asyncio.new_event_loop()

    with open(SETTINGS_FILE, "r", encoding="utf8") as file:
      shared.settings = json.load(file)
    
    shared.main_window.add_to_chat("Awaiting connection...")
    shared.client_thread.login()

    for _ in range(100):
      if shared.client_thread.tmi_client.logged: break
      else: time.sleep(0.1)
    if not shared.client_thread.tmi_client.logged: raise ConnectionError("Cannot connect! Try to restart the bot.")
    shared.main_window.add_to_chat("Connected !")

    for channel in shared.settings['bot_settings']['auto_join']:
      self.join_channel(channel, auto=True)
      self.handle_buffer()
    
    time.sleep(1) # TO BE SURE THE TABS ARE OPENED ON MAINWINDOW
    
    while True:
      self.handle_buffer()
      if shared.window_closed:
        for channel in shared.main_window.get_channels(): self.loop.run_until_complete(shared.client_thread.part(channel))
        shared.client_thread.logout()
        break
      time.sleep(0.1)
  
  def handle_buffer(self):
    while shared.history_buffer != []:
      if isinstance(shared.history_buffer[0], list):
        user, channel, message = shared.history_buffer[0]
        if message.startswith(shared.settings['bot_settings']['command_prefix']): shared.bot_commands_handler._handle_command(user, channel, message[1:])
        if shared.settings['bot_settings']['debug']: shared.main_window.add_to_chat(f"[DEBUG] {user}: {message}", channel)
      elif isinstance(shared.history_buffer[0], str):
        message = shared.history_buffer[0]
        if shared.settings['bot_settings']['debug']: shared.main_window.add_to_chat(f"[DEBUG] {message}")
      shared.history_buffer.remove(shared.history_buffer[0])

  def join_channel(self, channel: str, auto=False):
    channel = str("#"+channel).lower() if channel[0] != "#" else channel.lower()
    shared.main_window.add_to_chat(f"{'[Auto-Join] ' if auto else ''}Joining {channel}...")
    self.loop.run_until_complete(shared.client_thread.send_message(channel, shared.settings['bot_settings']['welcome_message']))
    self.loop.run_until_complete(shared.client_thread.join(channel))
    shared.main_window.add_tab(channel)
    shared.main_window.add_to_chat(f"Joined {channel} !")

  def leave_channel(self, channel: str):
    shared.main_window.add_to_chat(f"Leaving {channel}...")
    self.loop.run_until_complete(shared.client_thread.send_message(channel, shared.settings['bot_settings']['part_message']))
    self.loop.run_until_complete(shared.client_thread.part(channel))
    shared.main_window.remove_tab(channel)
    shared.main_window.add_to_chat(f"Leaved {channel} !")

  def send_to_channel(self, channel: str, message: str):
    self.loop.run_until_complete(shared.client_thread.send_message(channel, message))
    shared.main_window.add_to_chat(f"[BOT][{channel}]: {message}", channel)
