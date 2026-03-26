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

class Controller:
    CURRENT_VERSION = "v4.0.0"
    def __init__(self):
        self.different_version = False
        self.current_window = None
        self.root = ctk.CTk()
        self.root.withdraw()

        if os.path.exists("cache.txt"):
            self.show_cookie_window()
        else:
            self.show_cache_window()
    
    def show_settings(self):
        self.previous_window = self.current_window
        self.previous_window.withdraw()
        self.current_window = SettingsView(self.previous_window)
    
    def show_cache_window(self):
        self.close_current()
        self.current_window = CacheView(self)
    
    def show_cookie_window(self):
        self.close_current()
        self.current_window = CookieView(self)
    
    def show_main_window(self):
        self.close_current()
        self.current_window = MainView(self)
    
    def close_current(self):
        if self.current_window is not None:
            self.current_window.withdraw()
            self.current_window.after(50, self.current_window.destroy)
            self.current_window = None
    
class CacheView(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller

class CookieView(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        
class MainView(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller

class SettingsView(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        
class UpdatingView(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__(controller.root)
        self.controller = controller
        
class SettingsButtonFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller.root)
        self.controller = controller

class ThemeButtonFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller.root)
        self.controller = controller
        
class CacheModel:
    def __init__(self):
        pass

class CookieModel:
    def __init__(self):
        pass

class MainModel:
    def __init__(self):
        pass

class SettingsModel:
    def __init__(self):
        pass

class UpdatingModel:
    def __init__(self):
        pass

