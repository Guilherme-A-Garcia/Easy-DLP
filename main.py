from CTkMessagebox import CTkMessagebox
import customtkinter as ctk
import subprocess
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
    icon = 'icon.ico'
    try:
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(os.path.dirname(sys.executable), icon)
            if not os.path.exists(icon_path):
                icon_path = os.path.join(os.getcwd(), icon)
        else:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/EasyDLP.ico')
     
        if os.path.exists(icon_path):
            def set_icon():
                try:
                    root.iconbitmap(icon_path)
                except Exception as e:
                    print(f"Delayed icon set failed: {e}")
            root.after(190, set_icon)
    except Exception as e:
        print(f"Error, icon not available: {e}")

def err_msg(text):
    CTkMessagebox(title='Error', message=text, icon="cancel")
def info_msg(text):
    CTkMessagebox(title='Information', message=text, icon="info")

class EasyDLPApp:
    def __init__(self):
        self.current_window = None
        self.root = ctk.CTk()
        self.root.withdraw()
        self.final_cookie_selection = ctk.StringVar()

        if os.path.exists("cache.txt"):
            self.show_cookie_window()
        else:
            self.show_cache_window()
    
    def update_final_cookie_sel(self, new_val):
        self.final_cookie_selection.set(new_val)

    def clear_cache(self):
        self.result = CTkMessagebox(title='Confirmation', message='Clearing your YT-DLP path will close the application, would you like to continue?', option_1="No", option_2="Yes")
        try:
            if self.result.get() == "Yes":
                os.remove("cache.txt")
                self.root.destroy()
        except FileNotFoundError:
            pass

    def download(self, main_entry):
        LOGTXT_CONST = "log.txt"
        if not main_entry.get():
            err_msg('Please, insert a webpage link')
            return
        else:
            self.download_link = main_entry.get()
            with open("cache.txt", 'r') as file:
                self.path_from_cache = file.readline().strip()
            with open('download.bat', 'w') as file:
                file.write('@echo off\n')
                file.write(f'cd /d {self.path_from_cache}\n')
                self.selected_browser = self.final_cookie_selection.get()
                if self.selected_browser == 'None':
                    file.write(f'yt-dlp.exe --quiet --no-warnings {self.download_link}\n')
                else:
                    file.write(f'yt-dlp.exe --quiet --no-warnings --cookies-from-browser {self.selected_browser} {self.download_link}\n')
                file.write('exit\n')
        self.download_abs_path = os.path.abspath('download.bat')

        self.startupinfo = None
        if sys.platform.startswith("win"):
            self.startupinfo = subprocess.STARTUPINFO()
            self.startupinfo.wShowWindow = subprocess.SW_HIDE

        self.process = subprocess.Popen([self.download_abs_path], startupinfo=self.startupinfo, stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0)
        
        _, stderr = self.process.communicate()
        proc_success = self.process.returncode == 0
        self.process.wait()
        if proc_success:
            info_msg(f'File successfully downloaded. Check your YT-DLP folder: "{self.path_from_cache}".')
        else:
            if not os.path.exists(LOGTXT_CONST):
                with open(LOGTXT_CONST, 'w', encoding='utf-8') as file:
                    file.write(stderr.decode('utf-8', errors='ignore'))
                log_path = os.path.abspath(LOGTXT_CONST)
                err_msg(f'An error occurred during the download, a log file was generated at: {log_path}')
            else:
                with open(LOGTXT_CONST, 'w', encoding='utf-8') as file:
                    file.write(stderr.decode('utf-8', errors='ignore'))
                log_path = os.path.abspath(LOGTXT_CONST)
                err_msg(f'An error occurred during the download, a preexisting log file was updated at: {log_path}')
        os.remove(self.download_abs_path)

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
        dynamic_resolution(self, 500, 150)
        self.resizable(False,False)

        self.cache_main_lb = ctk.CTkLabel(self, text='Insert the path to your YT-DLP file', font=('', 20))
        self.cache_main_lb.pack(pady=(15, 0))

        self.cache_entry = ctk.CTkEntry(self, font=('', 14), insertwidth=1)
        self.cache_entry.pack(pady=(0, 5), fill="both", padx=20)
        simple_handling(self.cache_entry, "<Return>", self.cache_enter)

        self.cache_frame = ctk.CTkFrame(self)
        self.cache_frame.pack()
        self.cache_frame.grid_rowconfigure(0, weight=1)
        self.cache_frame.grid_columnconfigure(0, weight=1)

        self.cache_enter_b = ctk.CTkButton(self.cache_frame, text='Enter', font=('', 15), command=self.cache_enter)
        self.file_search_b = ctk.CTkButton(self.cache_frame, text='Search', font=('', 15), command=self.search_button)
        self.cache_enter_b.grid(row=0, column=0, padx=(0, 10))
        self.file_search_b.grid(row=0, column=1)
        simple_handling(self.cache_enter_b, "<Return>", self.cache_enter)
        simple_handling(self.file_search_b, "<Return>", self.search_button)
        
        self.cache_entry.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.attributes('-alpha', 1)
    
    def on_closing(self):
        self.confirmation = CTkMessagebox(title="Exit confirmation", message="Exit application?", icon='warning', option_1="No", option_2="Yes")
        if self.confirmation.get() == "Yes":
            self.destroy()
            self.app.root.destroy()

    def cache_enter(self):
        if not self.cache_entry.get():
            err_msg("Please, insert a path to your YT-DLP folder.")
        else:
            try:
                with open('cache.txt', 'w') as file:
                    file.write(self.cache_entry.get())
                self.app.show_cookie_window()
            except Exception as e:
                err_msg(f"Error: {e}")
    
    def search_button(self):
        self.path = ctk.filedialog.askdirectory(title='Select your YT-DLP folder')
        if self.path:
            self.cache_entry.insert(0, self.path)

class CookieWindow(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app

        self.bind("<Button-1>", lambda e: e.widget.focus())
        self.attributes('-alpha', 0)
        set_window_icon(self)
        self.final_cookie_selection = self.app.final_cookie_selection
        self.title('Cookie importation')
        dynamic_resolution(self, 500, 280)
        self.resizable(False,False)
        
        self.cookie_ntc2_label = ctk.CTkLabel(self, text='Note: You need to be logged-in on YouTube before doing this process.', font=('', 10))
        self.cookie_ntc2_label.pack(pady=(0, 5))

        self.cookie_main_labelp1 = ctk.CTkLabel(self, text='If you wish to bypass age restriction,', font=('', 17))
        self.cookie_main_labelp2 = ctk.CTkLabel(self, text='select your browser to import cookies from.', font=('', 17))
        self.cookie_main_labelp1.pack(pady=(15, 0))
        self.cookie_main_labelp2.pack(pady=(0, 15))

        self.cookie_import_options = ['None', 'brave', 'chrome', 'chromium', 'edge', 'firefox', 'opera', 'safari', 'vivaldi', 'whale']
        self.cookie_import_menu = ctk.CTkOptionMenu(self, values=self.cookie_import_options, state='readonly')
        self.cookie_import_menu.set('None')
        self.cookie_import_menu.pack(pady=(10, 0))

        self.cookie_ntc_label = ctk.CTkLabel(self, text='Select "None" to skip the cookie importation.', font=('', 10))
        self.cookie_ntc_label.pack(pady=(0, 5))

        self.cookie_button = ctk.CTkButton(self, text='Save', font=('', 20), command=self.cookie_next_button)
        self.cookie_button.pack(pady=15)
        simple_handling(self.cookie_button, "<Return>", self.cookie_next_button)
        
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
        self.confirmation = CTkMessagebox(title="Exit confirmation", message="Exit application?", icon='warning', option_1="No", option_2="Yes")
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
        dynamic_resolution(self, 500, 320)
        self.resizable(False,False)

        main_label = ctk.CTkLabel(self, text='Insert URL', font=('', 35))
        main_label.pack(pady=(25, 0))

        main_entry = ctk.CTkEntry(self, font=('', 14), insertwidth=1)
        main_entry.pack(pady=10, fill="x", padx=20)
        simple_handling(main_entry, "<Return>", lambda:self.app.download(main_entry))

        main_download = ctk.CTkButton(self, text='Download', font=('', 20), command=lambda:self.app.download(main_entry))
        main_download.pack(pady=10)
        simple_handling(main_download, "<Return>", lambda:self.app.download(main_entry))

        main_clear_dir = ctk.CTkButton(self, text='Clear path', font=('', 13), command=self.app.clear_cache)
        main_clear_dir.pack(pady=0)

        main_entry.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.attributes('-alpha', 1)
    
    def on_closing(self):
        self.confirmation = CTkMessagebox(title="Exit confirmation", message="Exit application?", icon='warning', option_1="No", option_2="Yes")
        if self.confirmation.get() == "Yes":
            self.destroy()
            self.app.root.destroy()

if __name__ == "__main__":
    main()
