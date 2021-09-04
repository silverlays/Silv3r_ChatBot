import threading, os, json
from typing import cast
import controllers.shared_data as shared
from controllers.bot_controller import BotController
from views.mainwindow import MainWindow


CREDENTIALS_FILE = os.path.join(os.getcwd(), "credentials.json")


with open(CREDENTIALS_FILE, "r", encoding="utf8") as file:
  shared.credentials = cast(dict, json.load(file))

shared.main_window = MainWindow()
shared.bot_thread = BotController()

main_window_thread = threading.Thread(name="MainWindow_Thread", target=shared.main_window.show)
main_window_thread.start()
main_window_thread.join(1)
bot_thread = threading.Thread(name="Bot_Thread", target=shared.bot_thread.execute_thread)
bot_thread.start()
main_window_thread.join()
bot_thread.join(5)
