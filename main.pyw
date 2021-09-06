import threading, os, json
import internals.dispatcher as dispatcher
import internals.tmi_handler as tmi_handler
import mainwindow


with open(os.path.join(os.getcwd(), "credentials.json"), "r", encoding="utf8") as file:
  tmi_handler.credentials = json.load(file)

main_window_thread = threading.Thread(name="MainWindow_Thread", target=mainwindow.show)
main_window_thread.start()
main_window_thread.join(1)
bot_thread = threading.Thread(name="Bot_Thread", target=dispatcher.execute_thread)
bot_thread.start()
main_window_thread.join()
bot_thread.join(5)
