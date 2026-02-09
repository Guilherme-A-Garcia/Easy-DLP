import os, sys, subprocess, tkinter as tk
from tkinter import Label, Entry, Tk, BOTH, Button, Frame, X, messagebox, filedialog, ttk

# Transitional file from procedural to OOP, bound to replace main.py

# Inject EasyDLPApp inside the window classes to operate it, use the old globals as class variables in op class

def main():
    app = EasyDLPApp()

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