from CTkMessagebox import CTkMessagebox
from PIL import Image, ImageTk
import customtkinter as ctk
import subprocess
import threading
import sys
import os

def main():
    ctk.set_appearance_mode("System")
    app = EasyDLPApp()
    app.root.mainloop()

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

class EasyDLPApp:
    def __init__(self):
        self.current_window = None
        self.playlist_directory = ''
        self.root = ctk.CTk()
        self.root.withdraw()
        self.mp4_checkbox_state = ctk.StringVar(value='off')
        self.mp3_checkbox_state = ctk.StringVar(value='off')
        self.final_cookie_selection = ctk.StringVar()

        if os.path.exists("cache.txt"):
            self.show_cookie_window()
        else:
            self.show_cache_window()
    
    def set_theme(self, location):
        self.location = location
        theme = self.location.themes.theme_variable.get()
        ctk.set_appearance_mode(theme)

    def update_final_cookie_sel(self, new_val):
        self.final_cookie_selection.set(new_val)

    def clear_cache(self):
        self.result = CTkMessagebox(title='Confirmation', message='Clearing your YT-DLP path will close the application, would you like to continue?', option_1="No", option_2="Yes", button_color="#950808", button_hover_color="#630202", border_width=1)
        try:
            if self.result.get() == "Yes":
                os.remove("cache.txt")
                self.root.destroy()
        except FileNotFoundError:
            err_msg("The cache file was either moved or deleted, closing application.\nPlease, re-open and follow the procedures.")
            self.root.destroy()

    def is_playlist(self):
        if self.playlist_directory != '':
            return True
        else:
            return False
        
    def is_mp4_conversion(self):
        if self.mp4_checkbox_state.get() == 'on':
            return True
        else:
            return False
    
    def is_mp3(self):
        if self.mp3_checkbox_state.get() == 'on':
            return True
        else:
            return False

    def download(self, main_entry):
        self.selected_browser = self.final_cookie_selection.get()
        
        if self.is_playlist:
            self.playlist_folder = self.playlist_directory

        if not main_entry.get():
            err_msg('Please, insert a webpage link')
            return
        
        if not os.path.exists("cache.txt"):
            err_msg('Cache file missing, closing application...\nPlease, re-open the application and follow the necessary procedures.')
            return self.root.destroy()
        
        self.download_link = main_entry.get()
        
        with open("cache.txt", 'r') as file:
            self.path_from_cache = file.readline().strip()
            
        self.cmd_parts = ['yt-dlp', '--quiet', '--no-warnings']
        
        if is_linux():
            self.cmd_parts[0] = './yt-dlp'

        if self.is_mp3():
            self.cmd_parts += ['--extract-audio', '--audio-format', 'mp3']
        
        if self.is_mp4_conversion():
            self.cmd_parts += ['-S', '+vcodec:h264', '--audio-format', 'aac', '--merge-output-format', 'mp4']
            
        if self.selected_browser != 'None':
            if is_linux():
                self.cmd_parts += ['--js-runtime', 'node', '--cookies-from-browser', self.selected_browser]
            else:
                self.cmd_parts += ['--cookies-from-browser', self.selected_browser]

        if not self.is_playlist():
            self.cmd_parts += ['--no-playlist', '--playlist-end', '1']
        else:
            if is_linux:
                self.cmd_parts += ['-o', f"{self.playlist_folder}/%(playlist)s/%(title)s.%(ext)s"]
            else:
                self.cmd_parts += ['-o', f"{self.playlist_folder}\\%%(playlist)s\\%%(title)s.%%(ext)s"]
        
        self.cmd_parts.append(self.download_link)
        
        self.download_thread(self.cmd_parts, self.path_from_cache, self.playlist_folder)
  
    def download_subprocess(self, cmd_parts, path_from_cache, playlist_folder):
        LOGTXT_CONST = "log.txt"
        
        if self.is_playlist():
            self.download_location = playlist_folder
        
        if sys.platform.startswith('win'):
            self.startupinfo = subprocess.STARTUPINFO()
            self.startupinfo.wShowWindow = subprocess.SW_HIDE
            self.creationflags=subprocess.CREATE_NO_WINDOW
        else:
            self.startupinfo = None
            self.creationflags = 0

        self.process = subprocess.Popen(cmd_parts, startupinfo=self.startupinfo, stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL, creationflags=self.creationflags, cwd=path_from_cache)
        _, stderr = self.process.communicate()
        proc_success = self.process.returncode == 0
        self.process.wait()
        if proc_success:
            if self.is_playlist():
                self.root.after(100, success_msg(f'Playlist successfully downloaded. Check the output location: "{self.download_location}".'))
            else:
                self.root.after(100, success_msg(f'File successfully downloaded. Check your YT-DLP folder: "{self.path_from_cache}".'))
            self.root.after(0, self.current_window.progress_bar.configure(mode="determinate"))
            self.root.after(0, self.current_window.progress_bar.set(0))
            self.current_window.progress_bar.configure(progress_color="#808080", fg_color="#808080")
        else:
            if not os.path.exists(LOGTXT_CONST):
                with open(LOGTXT_CONST, 'w', encoding='utf-8') as file:
                    file.write(stderr.decode('utf-8', errors='ignore'))
                log_path = os.path.abspath(LOGTXT_CONST)
                self.root.after(0, self.current_window.progress_bar.configure(mode="determinate"))
                self.root.after(0, self.current_window.progress_bar.set(0))
                self.current_window.progress_bar.configure(progress_color="#808080", fg_color="#808080")
                err_msg(f'An error occurred during the download, a log file was generated at: {log_path}')
                
            else:
                with open(LOGTXT_CONST, 'w', encoding='utf-8') as file:
                    file.write(stderr.decode('utf-8', errors='ignore'))
                log_path = os.path.abspath(LOGTXT_CONST)
                self.root.after(0, self.current_window.progress_bar.configure(mode="determinate"))
                self.root.after(0, self.current_window.progress_bar.set(0))
                self.current_window.progress_bar.configure(progress_color="#808080", fg_color="#808080")
                err_msg(f'An error occurred during the download, a preexisting log file was updated at: {log_path}')

    def download_thread(self, cmd_parts, path_from_cache, playlist_folder):
        
        def check_thread():
            if self.thread.is_alive():
                self.root.after(200, check_thread)
            else:
                self.enable_widgets()
                self.current_window.progress_bar['value'] = 0
                self.current_window.progress_bar.configure(progress_color="#808080", fg_color="#808080")
        
        self.disable_widgets()
        self.current_window.progress_bar.configure(progress_color="#770505", fg_color="#808080", mode="indeterminate")
        self.current_window.progress_bar.start()
                
        self.thread = threading.Thread(target=self.download_subprocess, args=(cmd_parts, path_from_cache, playlist_folder), daemon=True)
        self.thread.start()
        check_thread()
        
    def write_cache(self, rewrite:bool):
        try:
            self.path = ctk.filedialog.askdirectory(title='Select your YT-DLP folder')
            
            if not self.path or not os.path.exists(self.path):
                self.error = CTkMessagebox(icon='cancel', title="Error", message="Please, insert a valid path to proceed.", option_1="Cancel", option_2="Retry", option_focus=1, button_color="#950808", button_hover_color="#630202", border_width=1)
                if self.error.get() == "Retry":
                    return self.write_cache(rewrite=True)
                else:
                    return

            if rewrite:
                if os.path.exists('cache.txt'):
                    with open('cache.txt', 'w') as file:
                        file.write(self.path)
                        file.close()
                    success_msg("The YT-DLP path has been successfully rewritten!")
                else:
                    with open('cache.txt', 'w') as file:
                        file.write(self.path)
                        file.close()
                    success_msg("The YT-DLP path has been successfully written!")
            else:
                self.current_window.cache_entry.insert(0, self.path)
        
        except Exception as e:
            print(f"An error has occurred: {e}")
        
    def disable_widgets(self):
        try:
            widgets = (self.current_window.main_entry, self.current_window.settings_frame.menu, self.current_window.main_download)
            for widget in widgets:
                widget.configure(state="disabled")
        except AttributeError:
            pass
        
    def enable_widgets(self):
        try:
            widgets = (self.current_window.main_entry, self.current_window.main_clear_dir, self.current_window.main_download)
            for widget in widgets:
                widget.configure(state="normal")
        except AttributeError:
            pass

    def show_settings(self):
        self.previous_window = self.current_window
        self.previous_window.withdraw()
        self.current_window = SettingsWindow(self.previous_window, self)
        if self.playlist_directory != '':
            self.current_window.pl_checkbox_state.set('on')

    def show_cache_window(self):
        self.close_current()
        self.current_window = CacheWindow(self)
    
    def show_cookie_window(self):
        self.close_current()
        self.current_window = CookieWindow(self)
    
    def show_main_window(self):
        self.close_current()
        self.current_window = MainWindow(self)

    def close_current(self):
        if self.current_window is not None:
            self.current_window.withdraw()
            self.current_window.after(50, self.current_window.destroy)
            self.current_window = None
    
class CacheWindow(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app

        self.bind("<Button-1>", lambda e: e.widget.focus())
        self.attributes('-alpha', 0)

        set_window_icon(self)
        self.title('YT-DLP Path Directory Cache')
        dynamic_resolution(self, 500, 160)
        self.resizable(False,False)

        self.settings_frame = SettingsFrame(self, self.app)
        self.settings_frame.pack(anchor="w", padx=3)

        self.cache_main_lb = ctk.CTkLabel(self, text='Insert the path to your YT-DLP file', font=('', 25))
        self.cache_main_lb.pack(pady=(5))

        self.cache_entry = ctk.CTkEntry(self, font=('', 14), insertwidth=1)
        self.cache_entry.pack(pady=10, fill="both", padx=20)
        simple_handling(self.cache_entry, "<Return>", self.cache_enter)

        self.cache_frame = ctk.CTkFrame(self, bg_color="transparent", fg_color="transparent")
        self.cache_frame.pack()
        self.cache_frame.grid_rowconfigure(0, weight=1)
        self.cache_frame.grid_columnconfigure(0, weight=1)

        self.cache_enter_b = ctk.CTkButton(self.cache_frame, text='Enter', font=('', 15), command=self.cache_enter, fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.file_search_b = ctk.CTkButton(self.cache_frame, text='Search', font=('', 15), command=lambda:self.app.write_cache(rewrite=False), fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.cache_enter_b.grid(row=0, column=0, padx=(0, 10))
        self.file_search_b.grid(row=0, column=1)
        simple_handling(self.cache_enter_b, "<Return>", self.cache_enter)
        simple_handling(self.file_search_b, "<Return>", lambda:self.app.write_cache(rewrite=False))
        
        self.cache_entry.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.attributes('-alpha', 1)
    
    def on_closing(self):
        self.confirmation = CTkMessagebox(title="Exit confirmation", message="Exit application?", icon='warning', option_1="No", option_2="Yes", option_focus=1, button_color="#950808", button_hover_color="#630202", border_width=1)
        if self.confirmation.get() == "Yes":
            self.destroy()
            self.app.root.destroy()

    def cache_enter(self):
        if not self.cache_entry.get() or not os.path.exists(self.cache_entry.get()):
            err_msg("Please, insert a valid path to your YT-DLP folder.")
        else:
            try:
                with open('cache.txt', 'w') as file:
                    file.write(self.cache_entry.get())
                self.app.show_cookie_window()
            except Exception as e:
                err_msg(f"Error: {e}")

class CookieWindow(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app

        self.bind("<Button-1>", lambda e: e.widget.focus())
        self.attributes('-alpha', 0)
        set_window_icon(self)
        self.final_cookie_selection = self.app.final_cookie_selection
        self.title('Cookie importation')
        dynamic_resolution(self, 500, 258)
        self.resizable(False,False)

        self.settings_frame = SettingsFrame(self, self.app)
        self.settings_frame.pack(anchor="w", padx=3)

        self.cookie_main_labelp1 = ctk.CTkLabel(self, text='If you wish to bypass age restriction,', font=('', 22))
        self.cookie_main_labelp2 = ctk.CTkLabel(self, text='select your browser to import cookies from.', font=('', 22))
        self.cookie_main_labelp1.pack()
        self.cookie_main_labelp2.pack(pady=(0, 15))

        self.cookie_import_options = ['None', 'brave', 'chrome', 'chromium', 'edge', 'firefox', 'opera', 'safari', 'vivaldi', 'whale']
        self.cookie_import_menu = ctk.CTkOptionMenu(self, values=self.cookie_import_options, state='readonly', fg_color="#780606", button_color="#580909", font=('', 18))
        self.cookie_import_menu.set('None')
        self.cookie_import_menu.pack(pady=(5, 0))

        self.cookie_ntc_label = ctk.CTkLabel(self, text='Select "None" to skip the cookie importation.', font=('', 10))
        self.cookie_ntc_label.pack(pady=(0, 5))

        self.cookie_button = ctk.CTkButton(self, text='Next', font=('', 20), command=self.cookie_next_button, fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.cookie_button.pack(pady=10)
        simple_handling(self.cookie_button, "<Return>", self.cookie_next_button)

        self.cookie_ntc2_label = ctk.CTkLabel(self, text='Note: You need to be logged-in on YouTube before doing this process.', font=('', 10))
        self.cookie_ntc2_label.pack(pady=(0, 5))
        
        self.cookie_import_menu.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.attributes('-alpha', 1)
        
    def cookie_next_button(self):
        selected_value = self.cookie_import_menu.get()
        if 'None' not in selected_value:
            self.msg = info_msg('Tip: You might want to keep your browser of choice closed while downloading.')
        self.app.update_final_cookie_sel(selected_value)
        self.app.show_main_window()

    def on_closing(self):
        self.confirmation = CTkMessagebox(title="Exit confirmation", message="Exit application?", icon='warning', option_1="No", option_2="Yes", option_focus=1, button_color="#950808", button_hover_color="#630202", border_width=1)
        if self.confirmation.get() == "Yes":
            self.destroy()
            self.app.root.destroy()
    
class MainWindow(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        
        self.bind("<Button-1>", lambda e: e.widget.focus())
        self.attributes('-alpha', 0)

        set_window_icon(self)
        self.title('Easy-DLP')
        dynamic_resolution(self, 500, 220)
        self.resizable(False,False)

        self.settings_frame = SettingsFrame(self, self.app)
        self.settings_frame.pack(anchor="w", padx=3)

        self.main_label = ctk.CTkLabel(self, text='Insert URL', font=('', 35))
        self.main_label.pack()

        self.main_entry = ctk.CTkEntry(self, font=('', 14), insertwidth=1)
        self.main_entry.pack(pady=8, fill="x", padx=20)
        simple_handling(self.main_entry, "<Return>", lambda:self.app.download(self.main_entry))

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.pack()
        
        self.main_download = ctk.CTkButton(self.button_frame, text='Download', font=('', 18), command=lambda:self.app.download(self.main_entry), fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.main_download.grid(row=0, column=0, padx=10)
        simple_handling(self.main_download, "<Return>", lambda:self.app.download(self.main_entry))
        
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", height=15, corner_radius=10, progress_color="#808080", fg_color="#808080", mode="determinate", border_color="#1d0000", border_width=2)
        self.progress_bar['value'] = 0
        self.progress_bar.pack(pady=15, fill='both', padx=50)

        self.main_entry.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.attributes('-alpha', 1)
    
    def on_closing(self):
        self.confirmation = CTkMessagebox(title="Exit confirmation", message="Exit application?", icon='warning', option_1="No", option_2="Yes", option_focus=1, button_color="#950808", button_hover_color="#630202", border_width=1)
        if self.confirmation.get() == "Yes":
            self.destroy()
            self.app.root.destroy()
            
class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=2)
        self.rowconfigure(3, weight=1)
        self.columnconfigure((0,1), weight=1)
        
        self.current_mp4_value = ctk.StringVar(value=self.app.mp4_checkbox_state.get())
        self.current_mp3_value = ctk.StringVar(value=self.app.mp3_checkbox_state.get())
        
        self.bind("<Button-1>", lambda e: e.widget.focus())
        self.attributes('-alpha', 0)

        set_window_icon(self)
        self.title('Settings')
        dynamic_resolution(self, 500, 330)
        self.resizable(False,False)

        self.themes = ThemeFrame(self, self.app)
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
        
        self.mp4_checkbox = ctk.CTkCheckBox(self.checkbox_frame, text="Force MP4", onvalue='on', offvalue='off', font=('', 14), fg_color="#950808", hover_color="#630202", variable=self.current_mp4_value)
        self.mp4_checkbox.grid(sticky="w", column=0, row=1, padx=10, pady=10)
        
        self.mp3_checkbox = ctk.CTkCheckBox(self.checkbox_frame, text="Audio only (MP3)", onvalue='on', offvalue='off', font=('', 14), fg_color="#950808", hover_color="#630202", variable=self.current_mp3_value)
        self.mp3_checkbox.grid(sticky="w", column=0, row=2, padx=10)
        self.mp3_checkbox.bind("<Button-1>", self.mp3_handler)
        self.verify_mp3_checkbox()
        
        self.right_button_frame = ctk.CTkFrame(self)
        self.right_button_frame.rowconfigure((0,1,2), weight=1)
        self.right_button_frame.columnconfigure(0, weight=1)
        self.right_button_frame.grid(sticky="nsew", row=2, column=1)
        
        self.clear_dir = ctk.CTkButton(self.right_button_frame, text='Clear path', font=('', 18), width=50, command=self.app.clear_cache, fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.clear_dir.grid(row=0)
        simple_handling(self.clear_dir, "<Return>", self.app.clear_cache)
        self.rewrite = ctk.CTkButton(self.right_button_frame, text='Rewrite path', font=('', 18), width=50, command=lambda:self.app.write_cache(rewrite=True), fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.rewrite.grid(row=1)
        if hasattr(self.parent, 'cache_main_lb'):
            self.clear_dir.configure(state="disabled")
            self.rewrite.configure(state="disabled")
            
        self.save_button = ctk.CTkButton(self, text='Save Settings', font=('', 18), command=self.save_changes, fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.save_button.grid(sticky="ew", row=3, column=0, padx=(70,30))
        
        self.discard_button = ctk.CTkButton(self, text='Discard Settings', font=('', 18), command=self.save_changes, fg_color="#950808", hover_color="#630202", corner_radius=10, border_color="#440000", border_width=1)
        self.discard_button.grid(sticky="ew", row=3, column=1, padx=(30,70))

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.attributes('-alpha', 1)

    def save_changes(self):
        self.app.mp4_checkbox_state.set(self.current_mp4_value.get())
        self.app.mp3_checkbox_state.set(self.current_mp3_value.get())
        self.app.current_window = self.parent
        self.destroy()
        self.parent.deiconify()
    
    def discard_changes(self):
        self.app.playlist_directory = ''
        self.app.current_window = self.parent
        self.destroy()
        self.parent.deiconify()
    
    def mp3_disable_checkboxes(self):
        try:
            # checkboxes = [(self.current_window.mp4_checkbox, self.mp4_checkbox_state), 
            #               (self.current_window.placeholder, self.placeholder_variable)]
            # for checkbox, variable in checkboxes:
            self.current_mp4_value.set(value='off')
            self.mp4_checkbox.configure(state="disabled")
        except AttributeError:
            pass

    def mp3_enable_checkboxes(self):
        try:
            # checkboxes = [(self.current_window.mp4_checkbox, self.mp4_checkbox_state), 
            #               (self.current_window.placeholder, self.placeholder_variable)]
            # for checkbox, variable in checkboxes:
            self.mp4_checkbox.configure(state="normal")
        except AttributeError:
            pass
    
    def verify_mp3_checkbox(self):
        if self.current_mp3_value.get() == 'on':
            self.mp3_disable_checkboxes()
        else:
            self.mp3_enable_checkboxes()
        
    def on_closing(self):
        self.save = CTkMessagebox(title="Save settings", message="Save settings?", icon='warning', option_1="Cancel", option_2="No", option_3="Yes", option_focus=1, button_color="#950808", button_hover_color="#630202", border_width=1)
        if self.save.get() == "Yes":
            self.save_changes()
        elif self.save.get() == "No":
            self.discard_changes()
        else:
            return
        
    def mp3_handler(self, event):
        self.verify_mp3_checkbox()
    
    def playlist_handler(self, event):
        if self.pl_checkbox_state.get() == 'on':
            self.app.playlist_directory = str(ctk.filedialog.askdirectory(title="Choose the download location for the playlist")).strip('()')
        else:
            self.app.playlist_directory = ''
            
        if self.app.playlist_directory != '':
            if not os.path.exists(self.app.playlist_directory):
                err_msg("This directory does not exist.")
                self.app.playlist_directory = ''
                self.pl_checkbox_state.set('off')
        else:
            self.pl_checkbox_state.set('off')

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.app = app
        self.menu_image = ctk.CTkImage(Image.open("menu.png"), size=(25, 25))
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
                
        self.menu = ctk.CTkButton(self, image=self.menu_image, fg_color="transparent", bg_color="transparent", hover=False, text="", command=self.app.show_settings, width=0)
        self.menu.grid(row=0, column=0, padx=0)

class ThemeFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.app = app

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.initial_theme = ctk.get_appearance_mode()
        self.theme_variable = ctk.StringVar(value=self.initial_theme)
        self.theme_switch = ctk.CTkSwitch(self, text="Toggle themes (Dark/Light)", font=("", 14), progress_color="#630202", fg_color="#630202", variable=self.theme_variable, command=lambda: self.app.set_theme(parent), offvalue="Dark", onvalue="Light")
        self.theme_switch.grid(row=0, column=0, padx=0)

if __name__ == "__main__":
    main()
