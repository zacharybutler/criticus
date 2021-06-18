import json
import os
from pathlib import Path
import platform
import subprocess
import webbrowser

import PySimpleGUIQt as sg

import tendon.py.edit_settings as es

# pylint: disable=no-member
def get_config(fn = None) -> dict:
    if not fn:
        settings = es.get_settings()
        fn = settings['ce_config_fn']
    try:
        with open(fn, 'r', encoding='utf-8') as c:
            return json.load(c)
    except:
        sg.popup_quick_message('No config file found.\nBrowse for the Config File')
        return None

def save_config(config: dict, fn: str):
    with open(fn, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def layout():
    settings = es.get_settings()
    i_size = (30, 1)
    config = get_config()
    if not config:
        config = {'name': '', 'base_text': '', 'witnesses': []}

    settings_frame = [
        [sg.T('Project Title'), sg.I(config['name'], size=i_size, key='name')],
        [sg.T('Basetext'), sg.I(config['base_text'], size=i_size, key='basetext')],
        [sg.T('Witnesses'), sg.Listbox(config['witnesses'], select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, key='witnesses')],
        [sg.B('Add Witness', bind_return_key=True), sg.I('', key='wit_to_add'), sg.T(''), sg.B('Delete Selected')]
    ]

    return [
        [sg.T('Collation Config File'), sg.I(settings['ce_config_fn'], key='config_fn'), sg.FileBrowse(file_types=(('JSON Files', '*.json'),))],
        [sg.Frame('Collation Configuration', settings_frame)],
        [sg.B('Update'), sg.T(''), sg.B('Start Collation Editor'), sg.T(''), sg.B('Done', key='exit')]
    ]

def edit_config(values):
    config = get_config(values['config_fn'])
    if values['name'] != '':
        config['name'] = values['name']
    if values['basetext'] != '':
        config['base_text'] = values['basetext']
    sg.popup_quick_message('Configuration File Updated')
    save_config(config, values['config_fn'])

def update_window(window: sg.Window, values):
    config = get_config(values['config_fn'])
    if not config:
        return
    window['name'].update(config['name'])
    window['basetext'].update(config['base_text'])
    window['witnesses'].update(config['witnesses'])

def add_witness(values, window):
    if values['wit_to_add'] == '':
        return
    config = get_config(values['config_fn'])
    config['witnesses'].append(values['wit_to_add'])
    save_config(config, values['config_fn'])
    update_window(window, values)
    window['wit_to_add'].update('')

def remove_witnesses(values, window):
    if values['witnesses'] == []:
        return
    config = get_config(values['config_fn'])
    for wit in values['witnesses']:
        try:
            config['witnesses'].remove(wit)
        except:
            pass
    save_config(config, values['config_fn'])
    update_window(window, values)
    sg.popup_quick_message(f'Removed:\n{", ".join(values["witnesses"])}\n')

def start_ce(values):
    if values['config_fn'] == '':
        return
    cwd = os.getcwd()
    root_dir = Path(values['config_fn']).parent.parent.parent.parent.parent.as_posix()
    print(root_dir)
    os.chdir(root_dir)
    # try:
    if platform.system() == 'Windows':
        from subprocess import CREATE_NEW_CONSOLE
        subprocess.Popen('start startup.bat', shell=True, creationflags=CREATE_NEW_CONSOLE)
        subprocess.Popen('start firefox http://localhost:8080/collation', shell=True)
    else:
        subprocess.Popen('./startup.sh', shell=True)
        webbrowser.get('firefox').open('http:localhost:8080/collation')
    # except:
    #     print('cold not open browser')
    os.chdir(cwd)
    return

def configure_ce(font, icon):
    window = sg.Window('Configure Collation Editor', layout(), font=font, icon=icon)
    while True:
        event, values = window.read()
        if event in [None, sg.WINDOW_CLOSED, 'exit']:
            break
        elif event == 'Update':
            if values['config_fn'] == '':
                continue
            try:
                edit_config(values)
                update_window(window, values)
            except:
                sg.popup_quick_message('Are you sure that is the right config.json file?\nIt did not work.')
            es.edit_settings('ce_config_fn', values['config_fn'])
        elif event == 'Add Witness':
            add_witness(values, window)
        elif event == 'Delete Selected':
            remove_witnesses(values, window)
        elif event == 'Start Collation Editor':
            start_ce(values)
    window.close()
    return False
