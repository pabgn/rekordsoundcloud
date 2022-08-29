from cgitb import enable
import dearpygui.dearpygui as dpg
from utils import get_playlists
from translate import translate
from datetime import datetime
from os.path import exists


def library_selected(sender, app_data):
    location = app_data['file_path_name']
    dpg.set_value("library_location", location)

def songs_selected(sender, app_data):
    location = app_data['file_path_name']
    dpg.set_value("songs_location", location)

def update_progress(progress):
    dpg.configure_item("progress_bar", default_value=progress)

def print_output(text):
    dpg.set_value("output_status", text+"\n"+dpg.get_value("output_status")) 

def update_status(status):
    text = 'Downloading...'
    print(status)
    if status['status'] == 'fatal':
        print_output('[FATAL] {}'.format(status['message']))
    if status['status'] == 'error':
        print_output('[ERROR] {} : {}'.format(status['filename'], status['message']))
    if status['status'] == 'initial':
        print_output('Rekordbox library opened successfully. Total tracks: {} - Total SoundCloud tracks: {}'.format(status['total_tracks'], status['total_soundcloud_tracks']))
    if status['status'] == 'metadata':
        text = 'Locating '+status['filename']+' in SoundCloud...'      
    if status['status'] == 'downloading':
        text = 'Downloading '+status['filename']+' '+status['_percent_str']+' '+status['_eta_str']
        if 'preview' in str(status):
            print_output('[WARNING] {} is downloading as a preview. Check SoundCloud OAuth credentials and make sure you have an active subscription'.format(status['filename']))
    if status['status'] == 'finished':
        text = 'Finished downloading '+status['filename']
        print_output('[OK] {} translated'.format(status['filename']))
    if status['status'] == 'end':
        text = ''
        print_output("Translation finished at {}: {} tracks successful, {} with errors".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), status['converted'], status['errors']))
        update_progress(1)
        dpg.configure_item("translate_button", enabled=True)
    dpg.set_value("progress_text",text)


def start_translation():
    if exists(dpg.get_value("songs_location")) and exists(dpg.get_value("library_location")):
        dpg.configure_item("progress_bar", show=True)
        dpg.configure_item("output_status", show=True)
        print_output("Translation process started at "+ datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        translate(dpg.get_value("library_location"), dpg.get_value("songs_location"), update_progress, update_status)
        dpg.configure_item("translate_button", enabled=False)
    else:
        print_output("Invalid Rekordbox XML file or song directory")


def main_window():

    with dpg.file_dialog(directory_selector=False, show=False, callback=library_selected, id="file_dialog_id", width=500, height=300):
        dpg.add_file_extension(".xml")
    
    dpg.add_file_dialog(directory_selector=True, show=False, callback=songs_selected, id="songs_dialog_id", width=500, height=300)

    with dpg.window(pos=[0, 0], autosize=True, no_collapse=True, no_resize=True, no_close=True, no_move=True,
                    no_title_bar=True, tag="Primary Window"):

        with dpg.child_window(tag="youtube_link", border=False):
            dpg.add_text("Rekordbox Library XML:")
            with dpg.group(horizontal=True, width=0):
                dpg.add_input_text(tag="library_location", callback=None,
                                    on_enter=True, width=500, enabled=False)
                dpg.add_button(label="Browse...", callback=lambda: dpg.show_item("file_dialog_id"))

            dpg.add_spacer()
            dpg.add_text("Folder to save song files:")
            with dpg.group(horizontal=True, width=0):
                dpg.add_input_text(tag="songs_location", callback=None,
                                    on_enter=True, width=500, enabled=False)
                dpg.add_button(label="Browse...", callback=lambda: dpg.show_item("songs_dialog_id"))
            dpg.add_spacer()
            with dpg.group(horizontal=True, width=0):
                dpg.add_button(tag="translate_button",
                                label=f"Translate SoundCloud tracks to local files",
                                callback=start_translation, height=50, width=500)
            dpg.add_spacer()
            dpg.add_text(tag="progress_text")
            dpg.add_progress_bar(tag="progress_bar", width=580, show=False)
            dpg.add_input_text(tag="output_status", width=580, default_value="", multiline=True, enabled=False, show=False, height=180)


def load_gui():
    dpg.create_context()
    main_window()

    dpg.create_viewport(title="RekordSoundCloud Translator", width=600, height=400, resizable=False)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Primary Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    load_gui()