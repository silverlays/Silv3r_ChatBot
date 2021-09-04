import time
import PySimpleGUI as sg
import controllers.shared_data as shared


class MainWindow():
  window: sg.Window

  def show(self):
    sg.theme("DarkGrey9")

    commands_frame_layout = [
      [sg.Column([
        [sg.Button("JOIN", key="join_button", font=("Fixedsys", 10, "bold"), expand_x=True), sg.Button("PART", key="part_button", font=("Fixedsys", 10, "bold"), expand_x=True)]
      ])]
    ]

    layout = [
      [sg.TabGroup([[self.add_tab("status", update=False)]], key="tab_group", size=(900, 500))],
      [sg.Frame("Commands", commands_frame_layout)],
      [sg.Text("Connection status:"), sg.Text("disconnected", key="connection_status", text_color="red", justification="left")],
      [sg.Input(expand_x=True, key="input_command", font=("", 14, "bold"), focus=True), sg.Ok(">SEND<", key="send_button", font=("Fixedsys", 12, "bold"))]
    ]
    
    self.window = sg.Window("Silv3r ChatBot", layout, font=("Dialog", 10), finalize=True)

    while(True):
      event, values = self.window.read(100)
      #print(event, '//', values)      
      if event == sg.WIN_CLOSED:
        shared.window_closed = True
        break
      if event == "__TIMEOUT__":
        if shared.client_thread.tmi_client.logged: self.window['connection_status'].update("connected", text_color="green")
        else: self.window['connection_status'].update("disconnected", text_color="red")
      if event == "send_button" and values['input_command'] != "" and self.get_current_channel() and self.get_current_channel() != "status":
        shared.bot_thread.send_to_channel(self.get_current_channel(), values['input_command'])
        self.window['input_command'].update('')
      if event == "join_button":
        channel = sg.popup_get_text("Enter the channel to join:")
        if channel and channel != "": shared.bot_thread.join_channel(channel)
        elif channel == "": sg.popup_error("No channel specified!", no_titlebar=True)
      if event == "part_button" and self.get_current_channel() and self.get_current_channel() != "status": shared.bot_thread.leave_channel(self.get_current_channel())

  def add_to_chat(self, text, channel: str=None):
    try:
      formated_message = "["+(time.strftime('%H:%M:%S', time.localtime()))+"] " if shared.settings['bot_settings']['timestamp'] else ""
      formated_message += f"{text}\r\n"
      if channel: target_chat: sg.Multiline = shared.main_window.window[channel+'_chat']
      else: target_chat: sg.Multiline = shared.main_window.window['status_chat']
      target_chat.update(disabled=False)
      target_chat.update(formated_message, append=True)
      target_chat.update(disabled=True)
    except RuntimeError: pass

  def add_tab(self, tab_name, update=True):
    tab_layout = [ [sg.Multiline("", key=tab_name+"_chat", font=("", 10, "bold"), pad=(0, 1), expand_x=True, expand_y=True, no_scrollbar=True,autoscroll=True, disabled=True)] ]
    new_tab = sg.Tab(tab_name, tab_layout)
    if update:
      tab_group: sg.TabGroup = self.window['tab_group']
      tab_group.add_tab(new_tab)
    else: return new_tab
  
  def remove_tab(self, tab_name):
    tab_group: sg.TabGroup = self.window['tab_group']
    for row in tab_group.Rows:
      for element in row:
        element: sg.Tab
        if element.Title == tab_name:
          self.window.AllKeysDict.pop(tab_name+"_chat")
          tab_group.Rows.remove(row)
          element.TKFrame.destroy()
          break

  def get_current_channel(self):
    tab_group: sg.TabGroup = self.window['tab_group']
    tab = tab_group.get()
    return tab

  def get_channels(self):
    tab_group: sg.TabGroup = self.window['tab_group']
    channels = []
    for row in tab_group.Rows:
      for element in row:
        element: sg.Tab
        if element.Title != "status": channels.append(element.Title)
    return channels