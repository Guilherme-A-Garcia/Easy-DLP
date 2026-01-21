import os, sys, subprocess, tkinter
from tkinter import Label, Entry, Tk, BOTH, Button, Frame, X, messagebox, filedialog, ttk

cache_path = ''
cachetxt_const = "cache.txt"
logtxt_const = "log.txt"

# Globals

cache_entry = None
cacheroot = None
final_cookie_selection = None

def set_window_icon(root):
    """Runtime icon loading for Nuitka"""
    try:
        if getattr(sys, 'frozen', False):  # Checks if the application is running as a frozen executable
            icon_path = os.path.join(os.path.dirname(sys.executable), 'icon.ico') # noqa
            if not os.path.exists(icon_path):
                icon_path = os.path.join(os.getcwd(), 'icon.ico')
        else:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/EasyDLP.ico')

        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception as e:
        print(f"Error, icon not available: {e}")



def dynamic_resolution(d_root, d_width, d_height):
    screen_height = d_root.winfo_screenheight()
    screen_width = d_root.winfo_screenwidth()
    x = (screen_width // 2) - (d_width // 2)
    y = (screen_height // 2) - (d_height // 2)
    d_root.geometry(f"{d_width}x{d_height}+{x}+{y}")
    
def err_msg(text):
    tkinter.messagebox.showwarning(title='Error', message=text)
def info_msg(text):
    tkinter.messagebox.showinfo(title='Information', message=text)

def download():
    if not main_entry.get():
        err_msg('Please, insert a webpage link')
    else:
        download_link = main_entry.get()
        with open(cachetxt_const, 'r') as file:
            path_from_cache = file.readline().strip()
        with open('download.bat', 'w') as file:
            file.write('@echo off\n')
            file.write(f'cd /d {path_from_cache}\n')
            selected_browser = final_cookie_selection.get()
            if selected_browser == 'None':
                file.write(f'yt-dlp.exe --quiet --no-warnings {download_link}\n')
            else:
                file.write(f'yt-dlp.exe --quiet --no-warnings --cookies-from-browser {selected_browser} {download_link}\n')
            file.write('exit\n')
    download_abs_path = os.path.abspath('download.bat')

    startupinfo = None
    if sys.platform.startswith("win"):
        startupinfo = subprocess.STARTUPINFO()
        # startupinfo.dwFlags != subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

    process = subprocess.Popen([download_abs_path], startupinfo=startupinfo, stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0)
    
    _, stderr = process.communicate()
    proc_success = process.returncode == 0
    process.wait()
    if proc_success:
        info_msg(f'File successfully downloaded. Check your YT-DLP folder: "{path_from_cache}".')
    else:
        if not os.path.exists(logtxt_const):  # Log file generation in case of errors
            with open(logtxt_const, 'w', encoding='utf-8') as file:
                file.write(stderr.decode('utf-8', errors='ignore'))
            log_path = os.path.abspath(logtxt_const)
            err_msg(f'An error occurred during the download, a log file was generated at: {log_path}')
        else:
            with open(logtxt_const, 'w', encoding='utf-8') as file:
                file.write(stderr.decode('utf-8', errors='ignore'))
            log_path = os.path.abspath(logtxt_const)
            err_msg(f'An error occurred during the download, a preexisting log file was updated at: {log_path}')
    os.remove(download_abs_path)

def clear_cache():
    result = tkinter.messagebox.askokcancel(title='Confirmation', message='Clearing your YT-DLP path will close the application, would you like to continue?')
    if result:
        os.remove(cachetxt_const)
        mainroot.quit()

def cache_enter():
    if not cache_entry.get():
        err_msg("Please, insert a path to your YT-DLP folder.")
    else:
        try:
            with open('cache.txt', 'w') as file:
                file.write(cache_entry.get())
                cacheroot.destroy()
        except Exception as e:
            err_msg(f"Error: {e}")
def search_button():
    path = tkinter.filedialog.askdirectory(title='Select your YT-DLP folder')
    if path:
        cache_entry.insert(0, path)

def cache_window():
    global cache_entry
    global cacheroot
    cacheroot = Tk()
    cacheroot.withdraw()

    set_window_icon(cacheroot)
    cacheroot.title('YT-DLP Path Directory Cache')
    dynamic_resolution(cacheroot, 500, 150)
    cacheroot.resizable(False,False)

    cache_main_lb = Label(cacheroot, text='Insert the path to your YT-DLP file', font=('', 20))
    cache_main_lb.pack(pady=(15, 0))

    cache_entry = Entry(cacheroot, font=('', 14))
    cache_entry.pack(pady=(0, 5), fill=BOTH, padx=20)

    cache_frame = Frame(cacheroot)
    cache_frame.pack()
    cache_frame.grid_rowconfigure(0, weight=1)
    cache_frame.grid_columnconfigure(0, weight=1)

    cache_enter_b = Button(cache_frame, text='Enter', font=('', 15), command=cache_enter)
    file_search_b = Button(cache_frame, text='Search', font=('', 15), command=search_button)
    cache_enter_b.grid(row=0, column=0, padx=(0, 10))
    file_search_b.grid(row=0, column=1)

    cacheroot.deiconify()
    cacheroot.mainloop()

def cookie_import_window():
    global final_cookie_selection

    def cookie_next_button():
        selected_value = cookie_import_menu.get()
        if 'None' not in selected_value:
            info_msg('Tip: You might want to keep your browser of choice closed while downloading.')
        final_cookie_selection.set(selected_value)
        cookieroot.destroy()

    cookieroot = Tk()
    cookieroot.withdraw()
    set_window_icon(cookieroot)
    final_cookie_selection = tkinter.StringVar()
    cookieroot.title('Cookie importation')
    dynamic_resolution(cookieroot, 500, 280)
    cookieroot.resizable(False,False)
    
    cookie_ntc2_label = Label(cookieroot, text='Note: You need to be logged-in on YouTube before doing this process.', font=('', 10))
    cookie_ntc2_label.pack(pady=(0, 5))

    cookie_main_labelp1 = Label(cookieroot, text='If you wish to bypass age restriction,', font=('', 17))
    cookie_main_labelp2 = Label(cookieroot, text='select your browser to import cookies from.', font=('', 17))
    cookie_main_labelp1.pack(pady=(15, 0))
    cookie_main_labelp2.pack(pady=(0, 15))

    cookie_import_options = ['None', 'brave', 'chrome', 'chromium', 'edge', 'firefox', 'opera', 'safari', 'vivaldi', 'whale']
    cookie_import_menu = ttk.Combobox(cookieroot, values=cookie_import_options, state='readonly', font=('', 14))
    cookie_import_menu.set('None')
    cookie_import_menu.pack(pady=(10, 0))

    cookie_ntc_label = Label(cookieroot, text='Select "None" to skip the cookie importation.', font=('', 10))
    cookie_ntc_label.pack(pady=(0, 5))

    cookie_button = Button(cookieroot, text='Save', font=('', 20), command=cookie_next_button)
    cookie_button.pack(pady=15)

    cookieroot.deiconify()
    cookieroot.mainloop()


if __name__ == "__main__":
    
    if not os.path.exists('cache.txt'):
        cache_window()

    cookie_import_window()

    # Main instance
    mainroot = Tk()
    mainroot.withdraw()

    set_window_icon(mainroot)
    mainroot.title('Easy-DLP')
    dynamic_resolution(mainroot, 500, 320)
    mainroot.resizable(False,False)

    main_label = Label(mainroot, text='Insert URL', font=('', 35))
    main_label.pack(pady=(25, 0))

    main_entry = Entry(mainroot, font=('', 14))
    main_entry.pack(pady=10, fill=X, padx=20)

    main_download = Button(mainroot, text='Download', font=('', 20), command=download)
    main_download.pack(pady=10)

    main_clear_dir = Button(mainroot, text='Clear path', font=('', 13), command=clear_cache)
    main_clear_dir.pack(pady=0)

    mainroot.deiconify()
    mainroot.mainloop()
