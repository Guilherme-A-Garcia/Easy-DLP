import os, sys, subprocess, tkinter as tk
from tkinter import Label, Entry, Tk, BOTH, Button, Frame, X, messagebox, filedialog, ttk

# Transitional file from procedural to OOP, bound to replace main.py

# Inject EasyDLPApp inside the window classes to operate it, use the old globals as class variables in op class

def main():
    app = EasyDLPApp()

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
        
        self.root.mainloop()
    
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
    
class CookieWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
    
class MainWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app

if __name__ == "__main__":
    main()