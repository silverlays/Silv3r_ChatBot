from typing import Union
import models.bot_commands as BotCommands
from models.client_thread import ClientThread
from controllers.bot_controller import BotController
from views.mainwindow import MainWindow


main_window: MainWindow
bot_thread: BotController
client_thread: ClientThread
bot_commands_handler: BotCommands
credentials: dict
settings: dict[dict, dict, dict]
window_closed: bool = False
history_buffer: Union[list[str], list[list[str, str, str]]] = []