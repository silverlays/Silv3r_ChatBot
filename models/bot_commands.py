### MUST BE CORELATION WITH SETTINGS.JSON
### COMMANDS FUNCTIONS ARE IN BOTTOM OF THIS FILE ###

import asyncio


### PRIVATE VARIABLES (DO NOT EDIT !) ###
bot_thread = None
settings_commands = {}
settings_keywords = {}
loop = asyncio.new_event_loop()
### PRIVATE VARIABLES (DO NOT EDIT !) ###


### PRIVATE FUNCTION (DO NOT EDIT !) ###
def handle_command(user: str, channel: str, command: str):
  for c in settings_commands:
    command_name = command[:command.find(" ")] if command.find(" ") != -1 else command
    args_index = command.find(" ")
    command_args = command[args_index+1:] if args_index != -1 else ""
    if c == command_name: globals()[command_name](user, channel, command_args)
def __translate_callback_vars(callback_text: str, user: str, channel: str):
  return callback_text.replace("{user}", user).replace("{channel}", channel)
### PRIVATE FUNCTION (DO NOT EDIT !) ###



###
### START FUNCTIONS FROM SETTINGS.JSON
###
def quit(*args):
  user, channel, command_args = args
  callback_message = __translate_callback_vars(settings_commands['quit']['callback_message'], user, channel)
  bot_thread.send_to_channel(channel, callback_message)
  bot_thread.leave_channel(channel)


def help(*args):
  user, channel, command_args = args
  bot_thread.send_to_channel(channel, f"@{user} {settings_commands[command_args]['help']}")
###
### END FUNCTIONS FROM SETTINGS.JSON ###
###
