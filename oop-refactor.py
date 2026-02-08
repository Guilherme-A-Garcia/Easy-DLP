import os, sys, subprocess, tkinter as tk
from tkinter import Label, Entry, Tk, BOTH, Button, Frame, X, messagebox, filedialog, ttk

# Transitional file from procedural to OOP, bound to replace main.py

def main():
    app = EasyDLPApp()

class EasyDLPApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.root.mainloop()
    
    def show_cache_window(self):
        pass
    
    def show_cookie_window(self):
        pass
    
    def show_main_window(self):
        pass

    def close_current(self):
        pass
    
class CacheWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        pass
    
class CookieWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        pass
    
class MainWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        pass
    
if __name__ == "__main__":
    main()