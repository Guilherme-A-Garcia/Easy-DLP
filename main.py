from __future__ import annotations
from CTkMessagebox import CTkMessagebox
from PIL import Image, ImageTk
from bs4 import BeautifulSoup
import customtkinter as ctk
import urllib.request
import subprocess
import threading
import requests
import yt_dlp
import sys
import os

  # Next direction: DITCH YT-DLP BINARIES COMPLETELY; USE THE YT-DLP API INSTEAD!
  # To do that, replace command generation with option generation, ditch subprocess, keep OS verification;
  # Make a yt-dlp execution method, pass as target for threading;
  # Repurpose cache generation from yt-dlp location to download location

LEFT_CLICK = "<Button-1>"
CACHE_FILE = "cache.txt"
RETURN_KEY = "<Return>"

def main():
    ctk.set_appearance_mode("System")
    
    app_state = AppStateModel()
    cache_model = CacheModel()
    main_model = MainModel()
    settings_model = SettingsModel()
    updating_model = UpdatingModel()
    
    app = Controller(app_state, 
                     cache_model, 
                     main_model, 
                     settings_model,
                     updating_model)
    app.root.mainloop()

# ---------------- UTILITY FUNCTIONS ---------------- #

def dynamic_resolution(d_root, d_width, d_height):
    screen_height = d_root.winfo_screenheight()
    screen_width = d_root.winfo_screenwidth()
    x = (screen_width // 2) - (d_width // 2)
    y = (screen_height // 2) - (d_height // 2)
    d_root.geometry(f"{d_width}x{d_height}+{x}+{y}")

def simple_handling(widget, key, event):
    widget.bind(key, lambda e: event())

def get_icon(is_linux:bool):
    if is_linux:
        icon = 'icon.png'
    else:
        icon = 'icon.ico'

    if getattr(sys, 'frozen', False):
        icon_path = os.path.join(os.path.dirname(sys.executable), icon)
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.getcwd(), icon)
    else:
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), icon)
    return icon_path

def set_window_icon(root):
    """Runtime icon loading for Nuitka"""
    def win_set_icon():
        try:
            root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Failed setting delayed icon: {e}")
    
    try:
        if is_linux():
            icon_path = get_icon(True)
            
            if os.path.exists(icon_path):
                pil_img = Image.open(icon_path).convert("RGBA")
                imagetk = ImageTk.PhotoImage(pil_img)
                root.after(300, root.iconphoto(False, imagetk))

        else:
            icon_path = get_icon(False)
        
            if os.path.exists(icon_path):
                root.after(300, win_set_icon)
    except Exception as e:
        print(f"Error, icon not available: {e}")

def is_linux():
    return sys.platform.startswith('linux')

def err_msg(text):
    error = CTkMessagebox(title='Error', message=text, icon="cancel", option_focus=1, button_color="#950808", button_hover_color="#630202")
    error.get()

def info_msg(text):
    info = CTkMessagebox(title='Information', message=text, icon="info", option_focus=1, button_color="#950808", button_hover_color="#630202")
    info.get()
    
def success_msg(text):
    success = CTkMessagebox(title='Success', message=text, icon="check", option_focus=1, button_color="#950808", button_hover_color="#630202")
    success.get()

# ---------------- CONTROLLER ---------------- #

class Controller:
    def __init__(self, 
                 app_state: AppStateModel,
                 cache_model: CacheModel,
                 main_model: MainModel,
                 settings_model: SettingsModel,
                 updating_model: UpdatingModel):
        self.app_state = app_state
        self.cache_model = cache_model
        self.main_model = main_model
        self.settings_model = settings_model
        self.updating_model = updating_model

        self.root = ctk.CTk()
        self.root.withdraw()

        self.service_container = ServiceContainer(self, cache_model, main_model, settings_model, updating_model, app_state)

        self.service_container.window_manager._start_app()

    def download(self, url):
        self.service_container.downloader_service.download(url)

    def cache_enter(self, entry:str):
        self.service_container.cache_service.cache_enter(entry)

    def set_cookie_selection(self, value):
        self.service_container.cookie_service.set_cookie_selection(value)

    def filedialog_askdir(self, title):
        result = ctk.filedialog.askdirectory(title=title)
        return result

# ---------------- VIEWS ---------------- #

class CacheView(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        
        self.bind(LEFT_CLICK, lambda e: e.widget.focus())
        self.attributes('-alpha', 0)

        set_window_icon(self)
        self.title('Download Directory Cache')
        dynamic_resolution(self, 500, 160)
        self.resizable(False,False)

        self.settings_frame = SettingsButtonFrame(self, self.controller)
        self.settings_frame.pack(anchor="w", padx=3)

        self.cache_main_lb = ctk.CTkLabel(self, text='Set download directory', font=('', 25))
        self.cache_main_lb.pack(pady=(5))

        self.cache_entry = ctk.CTkEntry(self, font=('', 14), insertwidth=1)
        self.cache_entry.pack(pady=10, fill="both", padx=20)

        self.cache_frame = ctk.CTkFrame(self, bg_color="transparent", fg_color="transparent")
        self.cache_frame.pack()
        self.cache_frame.grid_rowconfigure(0, weight=1)
        self.cache_frame.grid_columnconfigure(0, weight=1)

        self.cache_enter_b = ctk.CTkButton(self.cache_frame, text='Enter', font=('', 15), fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.file_search_b = ctk.CTkButton(self.cache_frame, text='Search', font=('', 15), fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)

        self.cache_enter_b.grid(row=0, column=0, padx=(0, 10))
        self.file_search_b.grid(row=0, column=1)
        
        self.cache_entry.focus_set()
        self.attributes('-alpha', 1)

class CookieView(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller

        self.bind(LEFT_CLICK, lambda e: e.widget.focus())
        self.attributes('-alpha', 0)
        
        set_window_icon(self)
        self.title('Cookie importation')
        dynamic_resolution(self, 500, 258)
        self.resizable(False,False)

        self.settings_frame = SettingsButtonFrame(self, self.controller)
        self.settings_frame.pack(anchor="w", padx=3)

        self.cookie_main_labelp1 = ctk.CTkLabel(self, text='If you wish to bypass age restriction,', font=('', 22))
        self.cookie_main_labelp2 = ctk.CTkLabel(self, text='select your browser to import cookies from.', font=('', 22))
        self.cookie_main_labelp1.pack()
        self.cookie_main_labelp2.pack(pady=(0, 15))

        self.cookie_import_options = ['None', 'brave', 'chrome', 'chromium', 'edge', 'firefox', 'opera', 'safari', 'vivaldi', 'whale']
        self.cookie_import_menu = ctk.CTkOptionMenu(self, values=self.cookie_import_options, state='readonly', fg_color="#780606", button_color="#580909", font=('', 18), command=self.on_cookie_selected)
        self.cookie_import_menu.set('None')
        self.cookie_import_menu.pack(pady=(5, 0))

        self.cookie_ntc_label = ctk.CTkLabel(self, text='Select "None" to skip the cookie importation.', font=('', 10))
        self.cookie_ntc_label.pack(pady=(0, 5))

        self.cookie_button = ctk.CTkButton(self, text='Next', font=('', 20), fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.cookie_button.pack(pady=10)

        self.cookie_ntc2_label = ctk.CTkLabel(self, text='Note: You need to be logged-in on YouTube before doing this process.', font=('', 10))
        self.cookie_ntc2_label.pack(pady=(0, 5))
        
        self.cookie_import_menu.focus_set()
        self.attributes('-alpha', 1)
    
    def on_cookie_selected(self, current_value):
        self.controller.set_cookie_selection(current_value)

class MainView(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        
        self.bind(LEFT_CLICK, lambda e: e.widget.focus())
        self.attributes('-alpha', 0)

        set_window_icon(self)
        self.title('Easy-DLP')
        dynamic_resolution(self, 500, 220)
        self.resizable(False,False)

        self.settings_frame = SettingsButtonFrame(self, self.controller)
        self.settings_frame.pack(anchor="w", padx=3)

        self.main_label = ctk.CTkLabel(self, text='Insert URL', font=('', 35))
        self.main_label.pack()

        self.main_entry = ctk.CTkEntry(self, font=('', 14), insertwidth=1)
        self.main_entry.pack(pady=8, fill="x", padx=20)

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.pack()
        
        self.main_download = ctk.CTkButton(self.button_frame, text='Download', font=('', 18), fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.main_download.grid(row=0, column=0, padx=10)
        
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", height=15, corner_radius=10, progress_color="#808080", fg_color="#808080", mode="determinate", border_color="#1d0000", border_width=2)
        self.progress_bar['value'] = 0
        self.progress_bar.pack(pady=15, fill='both', padx=50)

        self.main_entry.focus_set()
        self.attributes('-alpha', 1)

    def disable_widgets(self):
        try:
            widgets = (self.main_entry, self.settings_frame.menu, self.main_download)
            for widget in widgets:
                widget.configure(state="disabled")
        except AttributeError:
            pass
        
    def enable_widgets(self):
        try:
            widgets = (self.main_entry, self.settings_frame.menu, self.main_download)
            for widget in widgets:
                widget.configure(state="normal")
        except AttributeError:
            pass

class SettingsView(ctk.CTkToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent
        
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=2)
        self.rowconfigure(3, weight=1)
        self.columnconfigure((0,1), weight=1)
        
        mp3, mp4, playlist = self.controller.service_container.settings_service.get_settings_states(playlist_dir=False)
        
        self.mp3_var = ctk.StringVar(value=mp3)
        self.mp4_var = ctk.StringVar(value=mp4)
        self.playlist_var = ctk.StringVar(value=playlist)
        
        self.bind(LEFT_CLICK, lambda e: e.widget.focus())
        self.attributes('-alpha', 0)

        set_window_icon(self)
        self.title('Settings')
        dynamic_resolution(self, 500, 330)
        self.resizable(False,False)

        self.themes = ThemeButtonFrame(self, self.controller)
        self.themes.grid(row=0, column=0, padx=5, sticky="nw")
        
        self.settings_label = ctk.CTkLabel(self, text="Settings", font=('', 35))
        self.settings_label.grid(sticky="nsew", row=1, columnspan=2)
        
        self.checkbox_frame = ctk.CTkFrame(self)
        self.checkbox_frame.rowconfigure((0,1,2), weight=1)
        self.checkbox_frame.columnconfigure(0, weight=1)
        self.checkbox_frame.grid(sticky="nsew", row=2, column=0)
        
        self.playlist_checkbox = ctk.CTkCheckBox(self.checkbox_frame, text="Playlist mode", onvalue='on', offvalue='off', font=('', 14), fg_color="#950808", hover_color="#630202", variable=self.playlist_var)
        self.playlist_checkbox.grid(sticky="w", column=0, row=0, padx=10)
        
        self.mp4_checkbox = ctk.CTkCheckBox(self.checkbox_frame, text="Force MP4", onvalue='on', offvalue='off', font=('', 14), fg_color="#950808", hover_color="#630202", variable=self.mp4_var)
        self.mp4_checkbox.grid(sticky="w", column=0, row=1, padx=10, pady=10)
        
        self.mp3_checkbox = ctk.CTkCheckBox(self.checkbox_frame, text="Audio only (MP3)", onvalue='on', offvalue='off', font=('', 14), fg_color="#950808", hover_color="#630202", variable=self.mp3_var)
        self.mp3_checkbox.grid(sticky="w", column=0, row=2, padx=10)
        
        self.right_button_frame = ctk.CTkFrame(self)
        self.right_button_frame.rowconfigure((0,1,2), weight=1)
        self.right_button_frame.columnconfigure(0, weight=1)
        self.right_button_frame.grid(sticky="nsew", row=2, column=1)
        
        self.clear_dir = ctk.CTkButton(self.right_button_frame, text='Clear path', font=('', 18), width=50, fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.clear_dir.grid(row=0)

        self.rewrite = ctk.CTkButton(self.right_button_frame, text='Rewrite path', font=('', 18), width=50, fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.rewrite.grid(row=1)
        if hasattr(self.parent, 'cache_main_lb'):
            self.clear_dir.configure(state="disabled")
            self.rewrite.configure(state="disabled")
            
        self.save_button = ctk.CTkButton(self, text='Save Settings', font=('', 18), fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.save_button.grid(sticky="ew", row=3, column=0, padx=(70,30))
        
        self.discard_button = ctk.CTkButton(self, text='Discard Settings', font=('', 18), fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.discard_button.grid(sticky="ew", row=3, column=1, padx=(30,70))

        self.attributes('-alpha', 1)
        
    def settings_set_theme(self, theme:str):
        ctk.set_appearance_mode(theme)

class UpdatingView(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        
        self.bind(LEFT_CLICK, lambda e: e.widget.focus())
        self.attributes('-alpha', 0)
        
        set_window_icon(self)
        dynamic_resolution(self, 450, 100)
        self.resizable(False, False)
        self.title('Updating...')
        
        self.progress_label1 = ctk.CTkLabel(self, text="Update in progress.", font=("", 20))
        self.progress_label1.pack()
        
        self.progress_label2 = ctk.CTkLabel(self, text="Please, don't close this window while the application is being updated.", font=("", 12))
        self.progress_label2.pack()
        
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", height=10, width=400, corner_radius=10, progress_color="#770505", fg_color="#808080", mode="indeterminate", border_color="#1d0000", border_width=1)
        self.progress_bar.pack(pady=10)
        self.progress_bar.start()
        
        self.attributes('-alpha', 1)

class SettingsButtonFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller.root
        self.parent = parent
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "menu.png")
        
        self.menu_image = ctk.CTkImage(Image.open(image_path), size=(25, 25))
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
                
        self.menu = ctk.CTkButton(self, image=self.menu_image, fg_color="transparent", bg_color="transparent", hover=False, text="", width=0)
        self.menu.grid(row=0, column=0, padx=0)

class ThemeButtonFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color='transparent')
        self.controller = controller
        self.parent = parent

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.initial_theme = ctk.get_appearance_mode()
        self.theme_variable = ctk.StringVar(value=self.initial_theme)
        self.theme_switch = ctk.CTkSwitch(self, text="Toggle themes (Dark/Light)", font=("", 14), progress_color="#630202", fg_color="#630202", offvalue="Dark", onvalue="Light")
        self.theme_switch.grid(row=0, column=0, padx=0)

# ---------------- MODELS ---------------- #   
 
class CacheModel:
    def cache_enter(self, cache_entry):
        if not cache_entry:
            raise InvalidBinaryDirectory("Please insert a directory for your downloads.")
        elif not os.path.exists(cache_entry):
            raise InvalidBinaryDirectory("Invalid directory.")
        else:
            with open(CACHE_FILE, 'w') as file:
                file.write(cache_entry)
    
    def write_cache(self, path):
        if not path or not os.path.exists(path):
            raise InvalidBinaryDirectory("Invalid directory.")
        
        with open(CACHE_FILE, 'w') as file:
            file.write(path)
            file.close()

class MainModel:
    def __init__(self):
        self.states = {'mp3': None, 'mp4': None, 'playlist_dir': None}
    
    def receive_states(self, mp3, mp4, playlist_dir):
        self.states['mp3'] = mp3
        self.states['mp4'] = mp4
        self.states['playlist_dir'] = playlist_dir
        print(f'States: {self.states}')
    
    def generate_command(self, url, cookies):
        if not url:
            raise EmptyURL("URL field is empty.")
        
        if not os.path.exists(CACHE_FILE):
            raise MissingCache('Cache file missing.\nPlease, enter your YT-DLP directory and try again.')
    
        with open(CACHE_FILE, 'r') as file:
            yt_dlp_dir = file.readline().strip()
        
        if not yt_dlp_dir or not os.path.exists(yt_dlp_dir):
            raise InvalidBinaryDirectory("Invalid YT-DLP directory in cache.")

        if is_linux():
            executable = os.path.join(yt_dlp_dir, 'yt-dlp')
        else:
            executable = os.path.join(yt_dlp_dir, 'yt-dlp.exe')
            if not os.path.exists(executable):
                executable = os.path.join(yt_dlp_dir, 'yt-dlp')
        
        if not os.path.exists(executable):
            raise InvalidBinaryDirectory(f"yt-dlp executable not found in:\n{yt_dlp_dir}")
        
        cmd_parts = [executable, '--quiet', '--no-warnings']
            
        if is_linux():
            cmd_parts[0] = './yt-dlp'
        
        if self.states.get('mp3') == 'on':
            cmd_parts += ['--extract-audio', '--audio-format', 'mp3']
        
        if self.states.get('mp4') == 'on':
            cmd_parts += ['-S', '+vcodec:h264', '--audio-format', 'aac', '--merge-output-format', 'mp4']
        
        if not self.states.get('playlist_dir'):
            cmd_parts += ['--no-playlist', '--playlist-end', '1']
        else:
            if is_linux():
                cmd_parts += ['-o', f"{self.states['playlist_dir']}/%(playlist)s/%(title)s.%(ext)s"]
            else:
                cmd_parts += ['-o', f"{self.states['playlist_dir']}\\%%(playlist)s\\%%(title)s.%%(ext)s"]
        
        if cookies and cookies != 'None':
            if is_linux():
                cmd_parts += ['--js-runtime', 'node', '--cookies-from-browser', cookies]
            else:
                cmd_parts += ['--cookies-from-browser', cookies]

        cmd_parts.append(url)
        print(f'Final command: {cmd_parts}')
        return (cmd_parts, yt_dlp_dir)

class SettingsModel:
    def clear_cache(self):
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
        else:
            raise MissingCache('The cache file was either moved or deleted. Closing application...\nPlease, follow the standard procedures after reopening the app.')

class UpdatingModel:
    def update_app(self):
        url =  ''
        file_path = ''
        cwd = self.get_app_directory()

        if os.path.exists(cwd):
            print("Resolved update directory:", cwd)

            if is_linux():
                url = 'https://github.com/Guilherme-A-Garcia/Easy-DLP/releases/latest/download/Easy-DLP-x86_64.AppImage'
                file_path = os.path.join(cwd, 'Easy-DLP-x86_64-NEW.AppImage')
            else:
                url = 'https://github.com/Guilherme-A-Garcia/Easy-DLP/releases/latest/download/Easy-DLP.exe'
                file_path = os.path.join(cwd, 'Easy-DLP-NEW.exe')

            print("Downloading to:", file_path)
            
            try:
                urllib.request.urlretrieve(url, file_path)
            except Exception as e:
                raise URLLibError(f"An error occurred while downloading the update, the application will close: {e}")

    def close_and_rename(self):
        if is_linux():
            new_file = 'Easy-DLP-x86_64-NEW.AppImage'
            file_name = 'Easy-DLP-x86_64.AppImage'

            cmd = ['sh', '-c', f'(sleep 1; mv "{new_file}" "{file_name}"; chmod +x "{file_name}"; exec "{os.path.abspath(file_name)}") >/dev/null 2>&1']
            
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True, close_fds=True)
            os._exit(0)
        else:
            cwd = self.get_app_directory()
            
            new_file = 'Easy-DLP-NEW.exe'
            file_name = 'Easy-DLP.exe'
            
            new_file_abs = os.path.join(cwd, new_file)
            file_name_abs = os.path.join(cwd, file_name)
            
            os.system(f'start /b cmd /c "timeout /nobreak > nul 2 & move /y "{new_file_abs}" "{file_name_abs}" >nul 2>&1 &"')
            os._exit(0)
            os.system('exit')

    def auto_version_fetch(self):
        try:
            req_url = "https://github.com/Guilherme-A-Garcia/Easy-DLP/releases/latest"
            req_response = requests.get(req_url)
            soup = BeautifulSoup(req_response.text, 'html.parser')
            git_version = soup.find('span', class_='css-truncate-target').text.strip()
            print(f'Version located in the latest GitHub Release: {git_version}')
            return git_version
            
        except Exception as e:
            print(e)

    def get_app_directory(self):
        if getattr(sys, 'frozen', False):
            try:
                path = os.path.abspath(sys.argv[0])
                dir_path = os.path.dirname(path)
                if os.path.exists(dir_path):
                    return dir_path
            except Exception:
                pass
            
            try:
                cwd = os.getcwd()
                if os.path.exists(cwd):
                    return cwd
            except Exception:
                pass
            
            try:
                temp_dir = os.path.dirname(sys.executable)
                parent = os.path.abspath(os.path.join(temp_dir, '..'))
                if os.path.exists(parent):
                    return parent
            except Exception:
                pass
        
        return os.getcwd()

class AppStateModel:
    def __init__(self):
        self.current_version = "v4.0.0"
        self.different_version = False

        self.cookie_selection = "None"
        
        self.mp3_state = 'off'
        self.mp4_state = 'off'
        
        self.playlist_state = 'off'
        self.playlist_directory = ''

# ---------------- SERVICES/MANAGERS ---------------- #

class ServiceContainer:
    def __init__(self, controller, cache_model, main_model, settings_model, updating_model, app_state):
        self.controller = controller
        self.cache_model = cache_model
        self.main_model = main_model
        self.settings_model = settings_model
        self.updating_model = updating_model
        self.app_state = app_state
        
        self.window_manager = WindowManager(self.controller.root, self.controller)
        self.downloader_service = DownloaderService(self.controller, self.main_model, self.window_manager)
        self.settings_service = SettingsService(self.controller, self.app_state, self.window_manager)
        self.update_service = UpdateService(self.updating_model, self.app_state, self.window_manager)
        self.cache_service = CacheService(self.controller, self.cache_model, self.window_manager)
        self.cookie_service = CookieService(self.window_manager, self.app_state)

class WindowManager:
    def __init__(self, root, controller):
        self.controller = controller
        self.root = root
        self.current_view = None
        self.previous_view = None

    def show_cache_window(self):
        self.close_current()
        self.current_view = CacheView(self.controller)
        self._wire_cache_window()

    def show_cookie_window(self):
        self.close_current()
        self.current_view = CookieView(self.controller)
        self._wire_cookie_window()

    def show_main_window(self):
        self.close_current()
        self.current_view = MainView(self.controller)
        self._wire_main_window()

    def show_settings(self):
        self.previous_view = self.current_view
        self.previous_view.withdraw()
        self.current_view = SettingsView(self.previous_view, self.controller)
        self._wire_settings_window()

    def show_updating_window(self):
        self.close_current()
        self.current_view = UpdatingView(self.controller)

    def on_closing(self, window:str=None):
        if not window:
            confirmation = CTkMessagebox(title="Exit confirmation", message="Exit application?", icon='warning', option_1="No", option_2="Yes", option_focus=1, button_color="#950808", button_hover_color="#630202", border_width=1)
            if confirmation.get() == "Yes":
                self.root.destroy()
            else:
                return
        elif window == 'settings':
            save_prompt = CTkMessagebox(title="Save settings", message="Save settings?", icon='warning', option_1="Cancel", option_2="No", option_3="Yes", option_focus=1, button_color="#950808", button_hover_color="#630202", border_width=1)
            choice = save_prompt.get()
            if choice == "Yes":
                self.controller.service_container.settings_service.save_settings_changes()
            elif choice == "No":
                self.previous_view.deiconify()
                self.close_current()
                self.current_view = self.previous_view
            else:
                return

    def close_current(self):
        if self.current_view is not None:
            self.current_view.withdraw()
            self.current_view.after(50, self.current_view.destroy)
            self.current_view = None

    def _get_theme(self):
        try:
            if hasattr(self.current_view, 'themes'):
                return self.current_view.themes.theme_variable.get()
        except Exception:
            pass

    def _start_app(self):
        self._show_initial_window()
        self.controller.service_container.update_service.auto_update_thread()

    def _show_initial_window(self):
        if os.path.exists(CACHE_FILE):
            self.show_cookie_window()
        else:
            self.show_cache_window()

    def _wire_cache_window(self):
        self.current_view.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.current_view.settings_frame.menu.configure(command=self.show_settings)
        self.current_view.cache_enter_b.configure(command=lambda: self.controller.cache_enter(self.current_view.cache_entry.get()))
        self.current_view.file_search_b.configure(command=lambda: self.controller.service_container.cache_service.write_cache(rewrite=False))
        simple_handling(self.current_view.cache_entry, RETURN_KEY,lambda: self.controller.cache_enter(self.current_view.cache_entry.get()))

    def _wire_cookie_window(self):
        self.current_view.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.current_view.settings_frame.menu.configure(command=self.show_settings)
        self.current_view.cookie_button.configure(command=self.controller.service_container.cookie_service.handle_cookie_next)
        simple_handling(self.current_view.cookie_button, RETURN_KEY, self.controller.service_container.cookie_service.handle_cookie_next)

    def _wire_main_window(self):
        self.current_view.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.current_view.settings_frame.menu.configure(command=self.show_settings)
        self.current_view.main_download.configure(command=lambda:self.controller.download(url=self.current_view.main_entry.get().strip()))
        simple_handling(self.current_view.main_entry, RETURN_KEY, lambda:self.controller.download(url=self.current_view.main_entry.get().strip()))

    def _wire_settings_window(self):
        self.current_view.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(window='settings'))
        
        self.current_view.save_button.configure(command=self.controller.service_container.settings_service.save_settings_changes)
        self.current_view.discard_button.configure(command=self.controller.service_container.settings_service.discard_settings_changes)
        
        self.current_view.mp3_checkbox.bind(LEFT_CLICK, self.controller.service_container.settings_service.mp3_handler)
        self.current_view.playlist_checkbox.bind(LEFT_CLICK, self.controller.service_container.settings_service.playlist_handler)
        
        self.current_view.themes.theme_switch.configure(variable=self.current_view.themes.theme_variable)
        self.current_view.themes.theme_switch.configure(command=lambda: self.controller.service_container.settings_service.set_theme())
        
        self.current_view.clear_dir.configure(command=self.controller.service_container.settings_service.clear_cache)
        self.current_view.rewrite.configure(command=lambda:self.controller.service_container.cache_service.write_cache(rewrite=True))
        
        self.controller.service_container.settings_service.verify_mp3_checkbox()

class DownloaderService:
    LOGTXT_CONST = 'log.txt'
    def __init__(self, controller, main_model, window_manager):
        self.controller = controller
        self.main_model = main_model
        self.window_manager = window_manager
    
    def download(self, url):
        cmd_parts = []
        path_from_cache = None
        
        try:
            self.main_model.receive_states(*self.controller.service_container.settings_service.get_settings_states(playlist_dir=True))
            cmd_parts, path_from_cache = self.main_model.generate_command(url, cookies=self.controller.app_state.cookie_selection)
            self.download_thread(cmd_parts, path_from_cache)
        except MissingCache as e:
            err_msg(text=f'Error: {e}')
            self.controller.service_container.cache_service.write_cache(rewrite=True)
            return
        except EmptyURL as e:
            err_msg(text=f'Error: {e}')
            return
        except Exception as e:
            err_msg(text=f'Unexpected error: {e}')
            return

    def download_thread(self, cmd_parts, path_from_cache):
        def check_thread():
            if self.thread.is_alive():
                self.controller.root.after(200, check_thread)
            else:
                self.window_manager.current_view.enable_widgets()
                self.window_manager.current_view.progress_bar['value'] = 0
                self.window_manager.current_view.progress_bar.configure(progress_color="#808080", fg_color="#808080")
        
        def worker():
            try:
                self.download_subprocess(cmd_parts, path_from_cache)
                self.controller.root.after(0, lambda: self._download_success(path_from_cache))
            except DownloadError as e:
                self.controller.root.after(0, lambda e=e: self._download_error(e))
            except Exception as e:
                self.controller.root.after(0, lambda e=e: self._download_error(e, unexpected=True))

        self.window_manager.current_view.disable_widgets()
        self.window_manager.current_view.progress_bar.configure(progress_color="#770505", fg_color="#808080", mode="indeterminate")
        self.window_manager.current_view.progress_bar.start()
                
        self.thread = threading.Thread(target=worker, daemon=True)
        self.thread.start()
            
        check_thread()

    def download_subprocess(self, cmd_parts, path_from_cache):
        if sys.platform.startswith('win'):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.wShowWindow = subprocess.SW_HIDE
            creationflags = subprocess.CREATE_NO_WINDOW
        else:
            startupinfo = None
            creationflags = 0
        
        self.process = subprocess.Popen(cmd_parts, startupinfo=startupinfo, stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL, creationflags=creationflags, cwd=path_from_cache)
        _, stderr = self.process.communicate()

        if self.process.returncode != 0:
            log_path = self._write_log(stderr)
            raise DownloadError(f'Download failed.\nLog path: {log_path}')

    def _write_log(self, stderr):
        with open(self.LOGTXT_CONST, 'w', encoding='utf-8') as file:
            file.write(stderr.decode('utf-8', errors='ignore'))
        return os.path.abspath(self.LOGTXT_CONST)

    def _download_success(self, cache):
        self.window_manager.current_view.enable_widgets()
        self.window_manager.current_view.progress_bar.stop()
        self.window_manager.current_view.progress_bar['value'] = 0
        self.window_manager.current_view.progress_bar.configure(progress_color="#808080", fg_color="#808080")
        if self.controller.app_state.playlist_state == 'off':
            success_msg(f"File successfully downloaded to {cache}")
        else:
            success_msg(f"Playlist successfully downloaded to {self.controller.app_state.playlist_directory}")

    def _download_error(self, error, unexpected=False):
        self.window_manager.current_view.enable_widgets()
        self.window_manager.current_view.progress_bar.stop()
        self.window_manager.current_view.progress_bar['value'] = 0
        self.window_manager.current_view.progress_bar.configure(progress_color="#808080", fg_color="#808080")
        
        if unexpected:
            err_msg(f'Unexpected error: {error}')
        else:
            err_msg(f'Error: {error}')

class SettingsService:
    def __init__(self, controller, app_state, window_manager):
        self.controller = controller
        self.app_state = app_state
        self.window_manager = window_manager

    def clear_cache(self):
        result = CTkMessagebox(title='Confirmation', message='Clearing your YT-DLP path will close the application, would you like to continue?', option_1="No", option_2="Yes", button_color="#950808", button_hover_color="#630202", border_width=1)
        if result.get() == "Yes":
            try:
                self.controller.settings_model.clear_cache()
                self.controller.root.destroy()
            except MissingCache as e:
                err_msg(f'Error: {e}')
                self.controller.root.destroy()

    def set_theme(self):
        theme = self.window_manager._get_theme()
        self.window_manager.current_view.settings_set_theme(theme)

    def playlist_handler(self, event):
        if self.window_manager.current_view.playlist_var.get() == 'on':
            self.app_state.playlist_directory = str(self.controller.filedialog_askdir(title='Choose the download location for the playlist')).strip()
        else:
            self.app_state.playlist_directory = ''
            
        if self.app_state.playlist_directory != '':
            if not os.path.exists(self.app_state.playlist_directory):
                err_msg(text='This directory does not exist.')
                self.app_state.playlist_directory = ''
                self.window_manager.current_view.playlist_var.set('off')
        else:
            self.window_manager.current_view.playlist_var.set('off')

    def mp3_handler(self, event):
        self.verify_mp3_checkbox()

    def mp3_disable_checkboxes(self):
        self.window_manager.current_view.mp4_var.set(value='off')
        self.app_state.mp4_state = 'off'
        self.window_manager.current_view.mp4_checkbox.configure(state='disabled')

    def mp3_enable_checkboxes(self):
        self.window_manager.current_view.mp4_checkbox.configure(state='normal')

    def verify_mp3_checkbox(self):
        if self.window_manager.current_view.mp3_checkbox.get() == 'on':
            self.mp3_disable_checkboxes()
        else:
            self.mp3_enable_checkboxes()

    def save_settings_changes(self):
        self.set_settings_states(*self.retrieve_settings_states())
        self.window_manager.current_view.destroy()
        self.window_manager.current_view.parent.deiconify()
        self.window_manager.current_view = self.window_manager.current_view.parent

    def discard_settings_changes(self):
        self.window_manager.previous_view.deiconify()
        self.window_manager.close_current()
        self.window_manager.current_view = self.window_manager.previous_view

    def set_settings_states(self, mp3, mp4, playlist):
        self.app_state.mp3_state = mp3
        self.app_state.mp4_state = mp4
        self.app_state.playlist_state = playlist

    def retrieve_settings_states(self):
        return self.window_manager.current_view.mp3_checkbox.get(), self.window_manager.current_view.mp4_checkbox.get(), self.window_manager.current_view.playlist_checkbox.get()

    def get_settings_states(self, playlist_dir:bool=False):
        return (self.app_state.mp3_state, self.app_state.mp4_state, self.app_state.playlist_state if not playlist_dir else self.app_state.playlist_directory)

class UpdateService:
    def __init__(self, updating_model, app_state, window_manager):
        self.updating_model = updating_model
        self.app_state = app_state
        self.window_manager = window_manager

    def auto_version_fetch(self):
        try:
            located_version = self.updating_model.auto_version_fetch()
            if located_version != self.app_state.current_version:
                self.app_state.different_version = True
        except Exception as e:
            err_msg(f'Unexpected error: {e}')

    def auto_update_thread(self):
        def update_thread(inputted_thread):
            if inputted_thread.is_alive():
                self.window_manager.current_view.after(10, lambda: update_thread(inputted_thread))
            else:
                print(f"Thread {inputted_thread} finished successfully!")
                if inputted_thread == self.thread1:
                    check_update()
        
        self.thread1 = threading.Thread(target=self.auto_version_fetch)
        self.thread1.start()
        update_thread(self.thread1)
        
        def check_update():
            if self.app_state.different_version:
                msg = CTkMessagebox(message="A newer version has been detected, would you like to update the app?", title='Update Detected', option_1="Yes", option_2="No", option_focus=2, button_color="#950808", button_hover_color="#630202")
                response = msg.get()
                if response == 'Yes':
                    self.window_manager.show_updating_window()
                    self.thread2 = threading.Thread(target=self.update_app)
                    self.thread2.start()
                    update_thread(self.thread2)
                else:
                    return

    def close_and_rename(self):
        try:
            self.updating_model.close_and_rename()
            if self.window_manager.current_view is not None:
                self.window_manager.current_view.destroy()
                self.root.destroy()
                sys.exit()
        except Exception as e:
            err_msg(f'Unexpected error: {e}')

    def update_app(self):
        try:
            self.updating_model.update_app()
            success_msg('Update finished successfully. Closing application...')
            self.close_and_rename()
        except URLLibError as e:
            err_msg(e)
            self.root.destroy()

class CacheService:
    def __init__(self, controller, cache_model, window_manager):
        self.controller = controller
        self.cache_model = cache_model
        self.window_manager = window_manager

    def cache_enter(self, cache_entry:str):
        path = cache_entry.strip()
        
        try:
            self.cache_model.cache_enter(path)
            self.window_manager.show_cookie_window()
        except InvalidBinaryDirectory as e:
            err_msg(f"Error: {e}")
        except Exception as e:
            err_msg(f"Unexpected error: {e}")

    def write_cache(self, rewrite:bool):
        path = self.controller.filedialog_askdir(title='Select the destination for your downloads')
        
        if rewrite:
            try:
                self.cache_model.write_cache(path=path)
                success_msg('Cache successfully rewritten!')
            except InvalidBinaryDirectory as e:
                err_msg(f'Error: {e}')
        else:
            self.window_manager.current_view.cache_entry.insert(0, path)

class CookieService:
    def __init__(self, window_manager, app_state):
        self.window_manager = window_manager
        self.app_state = app_state

    def set_cookie_selection(self, value):
        self.app_state.cookie_selection = value

    def handle_cookie_next(self):
        selection = self.app_state.cookie_selection
        
        if selection and selection != 'None':
            self.msg = CTkMessagebox(title='Information', message='Tip: You might want to keep your browser of choice closed while downloading.', icon="info", option_focus=1, button_color="#950808", button_hover_color="#630202")
            self.msg.get()
        self.window_manager.show_main_window()

# ---------------- EXCEPTIONS ---------------- #

class UserError(Exception):
    pass

class InvalidBinaryDirectory(UserError):
    pass

class EmptyURL(UserError):
    pass

class MissingCache(UserError):
    pass

class DownloadError(UserError):
    pass

class URLLibError(UserError):
    pass

if __name__ == "__main__":
    main()
