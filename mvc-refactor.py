from CTkMessagebox import CTkMessagebox
from PIL import Image, ImageTk
from bs4 import BeautifulSoup
import customtkinter as ctk
import urllib.request
import subprocess
import threading
import requests
import sys
import os

def main():
    ctk.set_appearance_mode("System")
    
    app_state = AppStateModel()
    cache_model = CacheModel()
    main_model = MainModel()
    
    app = Controller(app_state, cache_model, main_model)
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

def set_window_icon(root):
    """Runtime icon loading for Nuitka"""
    def win_set_icon():
        try:
            root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Failed setting delayed icon: {e}")
    
    try:
        if is_linux():
            if getattr(sys, 'frozen', False):
                icon_path = os.path.join(os.path.dirname(sys.executable), 'icon.png')
                if not os.path.exists(icon_path):
                    icon_path = os.path.join(os.getcwd(), 'icon.png')
            else:
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
            
            if os.path.exists(icon_path):
                pil_img = Image.open(icon_path).convert("RGBA")
                imagetk = ImageTk.PhotoImage(pil_img)
                root.after(300, root.iconphoto(False, imagetk))

        else:
            if getattr(sys, 'frozen', False):
                icon_path = os.path.join(os.path.dirname(sys.executable), 'icon.ico')
                if not os.path.exists(icon_path):
                    icon_path = os.path.join(os.getcwd(), 'icon.ico')
            else:
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
        
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
    CURRENT_VERSION = "v4.0.0"
    def __init__(self, app_state, cache_model, main_model):
        self.app_state = app_state
        self.cache_model = cache_model
        self.main_model = main_model
        self.different_version = False
        self.current_window = None
        self.root = ctk.CTk()
        self.root.withdraw()

        if os.path.exists("cache.txt"):
            self.show_cookie_window()
        else:
            self.show_cache_window()

    def controller_download(self, url):
        try:
            self.main_model.download(url, cookies=self.app_state.cookie_selection, options=None)
        except MissingCache as e:
            err_msg(text=f'Error: {e}')
            self.controller_write_cache(rewrite=True)
        except EmptyURL as e:
            err_msg(text=f'Error: {e}')

    def controller_cache_enter(self, cache_entry:str):
        path = cache_entry.strip()
        
        try:
            result = self.cache_model.cache_enter(path)
            if result["success"]:
                self.show_cookie_window()
            else:
                err_msg(f"Error: {result["error"]}")
        except InvalidBinaryDirectory as e:
            err_msg(f"Error: {e}")
    
    def controller_write_cache(self, rewrite:bool):
        path = self.filedialog_askdir(title='Select your YT-DLP folder')
        
        if rewrite:
            try:
                self.cache_model.write_cache(path=path)
            except InvalidBinaryDirectory:
                err_msg(f'Error: {e}')
        else:
            self.current_window.cache_entry.insert(0, path)

    def set_cookie_selection(self, value):
        self.app_state.cookie_selection = value
   
    def handle_cookie_next(self):
        selection = self.app_state.cookie_selection
        
        if selection and selection != 'None':
            self.msg = CTkMessagebox(title='Information', message='Tip: You might want to keep your browser of choice closed while downloading.', icon="info", option_focus=1, button_color="#950808", button_hover_color="#630202")
            self.msg.get()
        self.show_main_window()
    
    def filedialog_askdir(self, title):
        result = ctk.filedialog.askdirectory(title=title)
        return result
    
    def show_cache_window(self):
        self.close_current()
        self.current_window = CacheView(self)
        self.current_window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(next='cookie'))
        self.current_window.cache_enter_b.configure(command=lambda: self.controller_cache_enter(self.current_window.cache_entry.get()))
        self.current_window.file_search_b.configure(command=lambda: self.controller_write_cache(rewrite=False))
        simple_handling(self.current_window.cache_entry, "<Return>",lambda: self.controller_cache_enter(self.current_window.cache_entry.get()))

    def show_cookie_window(self):
        self.close_current()
        self.current_window = CookieView(self)
        self.current_window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(next='main'))
        self.current_window.cookie_button.configure(command=self.handle_cookie_next)
        simple_handling(self.current_window.cookie_button, "<Return>", self.handle_cookie_next)

    def show_main_window(self):
        self.close_current()
        self.current_window = MainView(self)
        self.current_window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing())
        self.current_window.main_download.configure(command=lambda:self.controller_download(url=self.current_window.main_entry.get().strip()))

    def show_settings(self):
        self.previous_window = self.current_window
        self.previous_window.withdraw()
        self.current_window = SettingsView(self.previous_window, self)

    def on_closing(self, next:str=None):
        self.confirmation = CTkMessagebox(title="Exit confirmation", message="Exit application?", icon='warning', option_1="No", option_2="Yes", option_focus=1, button_color="#950808", button_hover_color="#630202", border_width=1)
        if self.confirmation.get() == "Yes":
            self.root.destroy()
        else:
            return

    def close_current(self):
        if self.current_window is not None:
            self.current_window.withdraw()
            self.current_window.after(50, self.current_window.destroy)
            self.current_window = None

# ---------------- VIEWS ---------------- #

class CacheView(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        
        self.bind("<Button-1>", lambda e: e.widget.focus())
        self.attributes('-alpha', 0)

        set_window_icon(self)
        self.title('YT-DLP Path Directory Cache')
        dynamic_resolution(self, 500, 160)
        self.resizable(False,False)

        self.settings_frame = SettingsButtonFrame(self, self.controller)
        self.settings_frame.pack(anchor="w", padx=3)

        self.cache_main_lb = ctk.CTkLabel(self, text='Insert the path to your YT-DLP file', font=('', 25))
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

        self.bind("<Button-1>", lambda e: e.widget.focus())
        self.attributes('-alpha', 0)
        
        self.final_cookie_selection = ctk.StringVar()
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
        
        self.bind("<Button-1>", lambda e: e.widget.focus())
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
        
        # self.current_mp4_value = ctk.StringVar(value=self.app.mp4_checkbox_state.get())
        # self.current_mp3_value = ctk.StringVar(value=self.app.mp3_checkbox_state.get())
        
        self.bind("<Button-1>", lambda e: e.widget.focus())
        self.attributes('-alpha', 0)

        set_window_icon(self)
        self.title('Settings')
        dynamic_resolution(self, 500, 330)
        self.resizable(False,False)

        self.themes = ThemeFrame(self, self.controller)
        self.themes.grid(row=0, column=0, padx=5, sticky="nw")
        
        self.settings_label = ctk.CTkLabel(self, text="Settings", font=('', 35))
        self.settings_label.grid(sticky="nsew", row=1, columnspan=2)
        
        self.checkbox_frame = ctk.CTkFrame(self)
        self.checkbox_frame.rowconfigure((0,1,2), weight=1)
        self.checkbox_frame.columnconfigure(0, weight=1)
        self.checkbox_frame.grid(sticky="nsew", row=2, column=0)
        
        self.pl_checkbox_state = ctk.StringVar()
        self.playlist_checkbox = ctk.CTkCheckBox(self.checkbox_frame, text="Playlist mode", onvalue='on', offvalue='off', font=('', 14), fg_color="#950808", hover_color="#630202", variable=self.pl_checkbox_state)
        self.playlist_checkbox.grid(sticky="w", column=0, row=0, padx=10)
        self.playlist_checkbox.bind('<Button-1>', self.playlist_handler)
        
        # self.mp4_checkbox = ctk.CTkCheckBox(self.checkbox_frame, text="Force MP4", onvalue='on', offvalue='off', font=('', 14), fg_color="#950808", hover_color="#630202", variable=self.current_mp4_value)
        self.mp4_checkbox = ctk.CTkCheckBox(self.checkbox_frame, text="Force MP4", onvalue='on', offvalue='off', font=('', 14), fg_color="#950808", hover_color="#630202")
        self.mp4_checkbox.grid(sticky="w", column=0, row=1, padx=10, pady=10)
        
        # self.mp3_checkbox = ctk.CTkCheckBox(self.checkbox_frame, text="Audio only (MP3)", onvalue='on', offvalue='off', font=('', 14), fg_color="#950808", hover_color="#630202", variable=self.current_mp3_value)
        self.mp3_checkbox = ctk.CTkCheckBox(self.checkbox_frame, text="Audio only (MP3)", onvalue='on', offvalue='off', font=('', 14), fg_color="#950808", hover_color="#630202")
        self.mp3_checkbox.grid(sticky="w", column=0, row=2, padx=10)
        # self.mp3_checkbox.bind("<Button-1>", self.mp3_handler)
        self.verify_mp3_checkbox()
        
        self.right_button_frame = ctk.CTkFrame(self)
        self.right_button_frame.rowconfigure((0,1,2), weight=1)
        self.right_button_frame.columnconfigure(0, weight=1)
        self.right_button_frame.grid(sticky="nsew", row=2, column=1)
        
        # self.clear_dir = ctk.CTkButton(self.right_button_frame, text='Clear path', font=('', 18), width=50, command=self.app.clear_cache, fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.clear_dir = ctk.CTkButton(self.right_button_frame, text='Clear path', font=('', 18), width=50, fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.clear_dir.grid(row=0)
        # simple_handling(self.clear_dir, "<Return>", self.app.clear_cache)
        # self.rewrite = ctk.CTkButton(self.right_button_frame, text='Rewrite path', font=('', 18), width=50, command=lambda:self.app.write_cache(rewrite=True), fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.rewrite = ctk.CTkButton(self.right_button_frame, text='Rewrite path', font=('', 18), width=50, fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.rewrite.grid(row=1)
        if hasattr(self.parent, 'cache_main_lb'):
            self.clear_dir.configure(state="disabled")
            self.rewrite.configure(state="disabled")
            
        # self.save_button = ctk.CTkButton(self, text='Save Settings', font=('', 18), command=self.save_changes, fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.save_button = ctk.CTkButton(self, text='Save Settings', font=('', 18), fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.save_button.grid(sticky="ew", row=3, column=0, padx=(70,30))
        
        # self.discard_button = ctk.CTkButton(self, text='Discard Settings', font=('', 18), command=self.discard_changes, fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.discard_button = ctk.CTkButton(self, text='Discard Settings', font=('', 18), fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.discard_button.grid(sticky="ew", row=3, column=1, padx=(30,70))

        # self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.attributes('-alpha', 1)
        
class UpdatingView(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        
        self.bind("<Button-1>", lambda e: e.widget.focus())
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
                
        # self.menu = ctk.CTkButton(self, image=self.menu_image, fg_color="transparent", bg_color="transparent", hover=False, text="", command=self.app.show_settings, width=0)
        self.menu = ctk.CTkButton(self, image=self.menu_image, fg_color="transparent", bg_color="transparent", hover=False, text="", width=0)
        self.menu.grid(row=0, column=0, padx=0)

class ThemeButtonFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.initial_theme = ctk.get_appearance_mode()
        self.theme_variable = ctk.StringVar(value=self.initial_theme)
        # self.theme_switch = ctk.CTkSwitch(self, text="Toggle themes (Dark/Light)", font=("", 14), progress_color="#630202", fg_color="#630202", variable=self.theme_variable, command=lambda: self.app.set_theme(parent), offvalue="Dark", onvalue="Light")
        self.theme_switch = ctk.CTkSwitch(self, text="Toggle themes (Dark/Light)", font=("", 14), progress_color="#630202", fg_color="#630202", variable=self.theme_variable, offvalue="Dark", onvalue="Light")
        self.theme_switch.grid(row=0, column=0, padx=0)

# ---------------- MODELS ---------------- #   
 
class CacheModel:
    def __init__(self):
        pass
        
    def cache_enter(self, cache_entry):
        if not cache_entry:
            raise InvalidBinaryDirectory("Please insert the path to your YT-DLP binary directory.")
        elif not os.path.exists(cache_entry):
            raise InvalidBinaryDirectory("Invalid YT-DLP directory.")
        else:
            try:
                with open('cache.txt', 'w') as file:
                    file.write(cache_entry)
                return {"success": True}
            except Exception as e:
                return {'success': False, "error": str(e)}
    
    def write_cache(self, path):
        if not path or not os.path.exists(path):
            raise InvalidBinaryDirectory("Invalid YT-DLP directory path.")
        
        if os.path.exists('cache.txt'):
            with open('cache.txt', 'w') as file:
                file.write(path)
                file.close()
            return {'success': "The YT-DLP path has been successfully rewritten!"}
        else:
            with open('cache.txt', 'w') as file:
                file.write(path)
                file.close()
            return {'success': "The YT-DLP path has been successfully written!"} 

class MainModel:
    LOGTXT_CONST = 'log.txt'
    def __init__(self):
        pass
    
    def download(self, url, cookies, options=None):
        if not url:
            raise EmptyURL("URL field is empty.")
        
        if not os.path.exists("cache.txt"):
            raise MissingCache('Cache file missing.\nPlease, enter your YT-DLP directory and try again.')
    
        with open("cache.txt", 'r') as file:
            path_from_cache = file.readline().strip()
            file.close()
        
        cmd_parts = ['yt-dlp', '--quiet', '--no-warnings']
            
        if is_linux():
            cmd_parts[0] = './yt-dlp'
        
        if cookies is not None and cookies != 'None':
            if is_linux():
                cmd_parts += ['--js-runtime', 'node', '--cookies-from-browser', cookies]
            else:
                cmd_parts += ['--cookies-from-browser', cookies]

        cmd_parts.append(url)
        return (cmd_parts, path_from_cache)
    
    def _write_log(self, stderr):
        with open(MainModel.LOGTXT_CONST, 'w', encoding='utf-8') as file:
            file.write(stderr.decode('utf-8', errors='ignore'))
        return os.path.abspath(MainModel.LOGTXT_CONST)
    
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
        proc_success = self.process.returncode == 0

        if self.process.returncode != 0:
            log_path = self._write_log(stderr)
            raise DownloadError(f'Download failed.\nLog path: {log_path}')

class SettingsModel:
    def __init__(self):
        pass

class UpdatingModel:
    def __init__(self):
        pass

class AppStateModel:
    def __init__(self):
        self.cookie_selection = "None"

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

if __name__ == "__main__":
    main()
