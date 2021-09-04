import models.bot_commands as BotCommands
from typing import Union
from models.client_handler import ClientHandler
from controllers.bot_controller import BotController
from views.mainwindow import MainWindow


main_window: MainWindow
bot_controller: BotController
client_handler: ClientHandler
bot_commands_handler: BotCommands
credentials: dict
settings: dict[dict, dict, dict]
window_closed: bool = False
history_buffer: Union[list[str], list[list[str, str, str]]] = []