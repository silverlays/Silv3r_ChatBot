import time
import PySimpleGUI as sg
import views.mainwindow as main_window
import controllers.bot_handler as bot_handler


window: sg.Window = None
window_closed = False


def show():
  global window
  sg.theme("DarkGrey9")

  commands_frame_layout = [
    [sg.Column([
      [sg.Button("JOIN", key="join_button", font=("Fixedsys", 10, "bold"), expand_x=True), sg.Button("PART", key="part_button", font=("Fixedsys", 10, "bold"), expand_x=True)]
    ])]
  ]

  layout = [
    [sg.TabGroup([[add_tab("status", update=False)]], key="tab_group", size=(900, 500))],
    [sg.Frame("Commands", commands_frame_layout)],
    [sg.Text("Connection status:"), sg.Text("disconnected", key="connection_status", text_color="red", justification="left")],
    [sg.Input(expand_x=True, key="input_command", font=("", 14, "bold"), focus=True), sg.Ok(">SEND<", key="send_button", font=("Fixedsys", 12, "bold"))]
  ]
  
  window = sg.Window("Silv3r ChatBot", layout, font=("Dialog", 10), finalize=True)

  while(True):
    event, values = window.read(100)
    #print(event, '//', values)
    if event == sg.WIN_CLOSED:
      main_window.window_closed = True
      break
    if event == "__TIMEOUT__":
      if bot_handler.logged: window['connection_status'].update("connected", text_color="green")
      else: window['connection_status'].update("disconnected", text_color="red")
    if event == "send_button" and values['input_command'] != "" and get_current_channel() and get_current_channel() != "status":
      bot_handler.send_to_channel(get_current_channel(), values['input_command'])
      window['input_command'].update('')
    if event == "join_button":
      channel = sg.popup_get_text("Enter the channel to join:")
      if channel and channel != "": bot_handler.join_channel(channel)
      elif channel == "": sg.popup_error("No channel specified!", no_titlebar=True)
    if event == "part_button" and get_current_channel() and get_current_channel() != "status": bot_handler.leave_channel(get_current_channel())


def add_to_chat(text, channel: str=None):
  try:
    formated_message = "["+(time.strftime('%H:%M:%S', time.localtime()))+"] " if bot_handler.settings['bot_settings']['timestamp'] else ""
    formated_message += f"{text}\r\n"
    if channel and get_channels().index(channel): target_chat: sg.Multiline = main_window.window[channel+'_chat']
    else: target_chat: sg.Multiline = main_window.window['status_chat']
    target_chat.update(disabled=False)
    target_chat.update(formated_message, append=True)
    target_chat.update(disabled=True)
  except RuntimeError: pass
  except ValueError: pass


def add_tab(tab_name, update=True):
  tab_layout = [ [sg.Multiline("", key=tab_name+"_chat", font=("", 10, "bold"), pad=(0, 1), expand_x=True, expand_y=True, no_scrollbar=True,autoscroll=True, disabled=True)] ]
  new_tab = sg.Tab(tab_name, tab_layout)
  if update:
    tab_group: sg.TabGroup = window['tab_group']
    tab_group.add_tab(new_tab)
  else: return new_tab


def remove_tab(tab_name):
  tab_group: sg.TabGroup = window['tab_group']
  for row in tab_group.Rows:
    for element in row:
      element: sg.Tab
      if element.Title == tab_name:
        window.AllKeysDict.pop(tab_name+"_chat")
        tab_group.Rows.remove(row)
        element.TKFrame.destroy()
        break


def get_current_channel():
  tab_group: sg.TabGroup = window['tab_group']
  tab = tab_group.get()
  return tab


def get_channels():
  tab_group: sg.TabGroup = window['tab_group']
  channels = []
  for row in tab_group.Rows:
    for element in row:
      element: sg.Tab
      if element.Title != "status": channels.append(element.Title)
  return channels