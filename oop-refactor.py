import os, sys, subprocess, tkinter as tk
from tkinter import Label, Entry, Tk, BOTH, Button, Frame, X, messagebox, filedialog, ttk

# Transitional file from procedural to OOP, bound to replace main.py

# Inject EasyDLPApp inside the window classes to operate it, use the old globals as class variables in op class

def main():
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
            root.iconbitmap(icon_path)
    except Exception as e:
        print(f"Error, icon not available: {e}")

def err_msg(text):
    messagebox.showwarning(title='Error', message=text)
def info_msg(text):
    messagebox.showinfo(title='Information', message=text)

class EasyDLPApp:
    def __init__(self):
        self.current_window = None
        self.root = tk.Tk()
        self.root.withdraw()
        self.show_cache_window()
    
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
            self.current_window.destroy()
            self.current_window = None
    
class CacheWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app

        if not os.path.exists('cache.txt'):
            self.bind("<Button-1>", lambda e: e.widget.focus())
            self.attributes('-alpha', 0)

            set_window_icon(self)
            self.title('YT-DLP Path Directory Cache')
            dynamic_resolution(self, 500, 150)
            self.resizable(False,False)

            self.cache_main_lb = Label(self, text='Insert the path to your YT-DLP file', font=('', 20))
            self.cache_main_lb.pack(pady=(15, 0))

            self.cache_entry = Entry(self, font=('', 14), insertwidth=1)
            self.cache_entry.pack(pady=(0, 5), fill=BOTH, padx=20)
            simple_handling(self.cache_entry, "<Return>", self.cache_enter)

            self.cache_frame = Frame(self)
            self.cache_frame.pack()
            self.cache_frame.grid_rowconfigure(0, weight=1)
            self.cache_frame.grid_columnconfigure(0, weight=1)

            self.cache_enter_b = Button(self.cache_frame, text='Enter', font=('', 15), command=self.cache_enter)
            self.file_search_b = Button(self.cache_frame, text='Search', font=('', 15), command=self.search_button)
            self.cache_enter_b.grid(row=0, column=0, padx=(0, 10))
            self.file_search_b.grid(row=0, column=1)
            simple_handling(self.cache_enter_b, "<Return>", self.cache_enter)
            simple_handling(self.file_search_b, "<Return>", self.search_button)
            
            self.cache_entry.focus_set()
            self.attributes('-alpha', 1)
    
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
        self.path = filedialog.askdirectory(title='Select your YT-DLP folder')
        if self.path:
            self.cache_entry.insert(0, self.path)

class CookieWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app

        self.bind("<Button-1>", lambda e: e.widget.focus())
        self.attributes('-alpha', 0)
        set_window_icon(self)
        self.final_cookie_selection = tk.StringVar()
        self.title('Cookie importation')
        dynamic_resolution(self, 500, 280)
        self.resizable(False,False)
        
        self.cookie_ntc2_label = Label(self, text='Note: You need to be logged-in on YouTube before doing this process.', font=('', 10))
        self.cookie_ntc2_label.pack(pady=(0, 5))

        self.cookie_main_labelp1 = Label(self, text='If you wish to bypass age restriction,', font=('', 17))
        self.cookie_main_labelp2 = Label(self, text='select your browser to import cookies from.', font=('', 17))
        self.cookie_main_labelp1.pack(pady=(15, 0))
        self.cookie_main_labelp2.pack(pady=(0, 15))

        self.cookie_import_options = ['None', 'brave', 'chrome', 'chromium', 'edge', 'firefox', 'opera', 'safari', 'vivaldi', 'whale']
        self.cookie_import_menu = ttk.Combobox(self, values=self.cookie_import_options, state='readonly', font=('', 14))
        self.cookie_import_menu.set('None')
        self.cookie_import_menu.pack(pady=(10, 0))

        self.cookie_ntc_label = Label(self, text='Select "None" to skip the cookie importation.', font=('', 10))
        self.cookie_ntc_label.pack(pady=(0, 5))

        self.cookie_button = Button(self, text='Save', font=('', 20))  # command=self.cookie_next_button
        self.cookie_button.pack(pady=15)
        # simple_handling(self.cookie_button, "<Return>", self.cookie_next_button)
        
        self.cookie_import_menu.focus_set()
        self.attributes('-alpha', 1)
    
class MainWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app

if __name__ == "__main__":
    main()