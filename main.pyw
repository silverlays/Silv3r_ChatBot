import threading, os, json
import controllers.bot_handler as bot_handler
import models.bot_client_handler as bot_client_handler
import views.mainwindow as main_window
from typing import cast


with open(os.path.join(os.getcwd(), "credentials.json"), "r", encoding="utf8") as file:
  bot_client_handler.credentials = json.load(file)

main_window_thread = threading.Thread(name="MainWindow_Thread", target=main_window.show)
main_window_thread.start()
main_window_thread.join(1)
bot_thread = threading.Thread(name="Bot_Thread", target=bot_handler.execute_thread)
bot_thread.start()
main_window_thread.join()
bot_thread.join(5)
