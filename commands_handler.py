### MUST BE CORELATION WITH SETTINGS.JSON
### COMMANDS FUNCTIONS ARE IN BOTTOM OF THIS FILE ###

import asyncio
import internals.dispatcher as dispatcher

### PRIVATE VARIABLES (DO NOT EDIT !) ###
#_loop = asyncio.new_event_loop()
settings_commands = {}
settings_keywords = {}
_user, _channel, _command_args = ("", "", "")
### PRIVATE VARIABLES (DO NOT EDIT !) ###


### PRIVATE FUNCTION (DO NOT EDIT !) ###
def handle_command(user: str, channel: str, command: str):
  global settings_commands, settings_keywords, _user, _channel, _command_args
  _user = user
  _channel = channel
  settings_commands = dispatcher.settings['bot_commands']
  settings_keywords = dispatcher.settings['bot_keywords']
  user = user,
  for c in settings_commands:
    command_name = command[:command.find(" ")] if command.find(" ") != -1 else command
    args_index = command.find(" ")
    _command_args = command[args_index+1:] if args_index != -1 else ""    
    if c == command_name:
      globals()[command_name]()
      break
def _translate_callback_vars(callback_text: str, user: str, channel: str):
  return callback_text.replace("{user}", user).replace("{channel}", channel)
### PRIVATE FUNCTION (DO NOT EDIT !) ###



###
### START FUNCTIONS FROM SETTINGS.JSON
###
def commands():
  message = "Liste des commandes:"
  for c in settings_commands:
    message += f" !{c}"
  message += "."
  dispatcher.send_to_channel(_channel, message)


def quit():
  callback_message = _translate_callback_vars(settings_commands['quit']['callback_message'], _user, _channel)
  dispatcher.send_to_channel(_channel, callback_message)
  dispatcher.leave_channel(_channel)


def help():
  global _command_args
  if _command_args == "": _command_args = "help"
  dispatcher.send_to_channel(_channel, f"@{_user} {settings_commands[_command_args]['help']}")
###
### END FUNCTIONS FROM SETTINGS.JSON ###
###
