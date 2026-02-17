![Python](https://img.shields.io/badge/python-3.9+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Windows](https://img.shields.io/badge/platform-Windows-blue)
![GitHub release](https://img.shields.io/github/v/release/Guilherme-A-Garcia/Easy-DLP)

# Easy-DLP
Easy-DLP is a clean and simple GUI wrapper for **YT-DLP**. Download videos easily with browser cookie support.<br>
This application is but a humble wrapper coded in Python, using the following libraries: CustomTkinter, CTkMessagebox, subprocess, os and sys.<br>
The [binaries](https://github.com/Guilherme-A-Garcia/Easy-DLP/releases) are currently compiled with [Nuitka](https://nuitka.net/).

>[!CAUTION]
>By using this GUI, you agree to abide by local copyright laws. This project does not condone or encourage the unauthorized distribution of copyrighted material.

## Table of Contents
- [Preview](#preview)
- [Current Features](#current-features)
- [Requirements](#requirements)
- [How to Use](#how-to-use)
- [Roadmap](#roadmap)
- [Contributing](#contributing)

## Preview
![Main interface](assets/previews/Main.png)<br>
![Importing cookies interface](assets/previews/Cookie.png)

## Current Features
- Simple and easily manageable GUI
- Browser cookie import (for age-restricted content)
- Remembers the last YT-DLP binary location (simple .txt soft-cache system)
- Error handling with user-friendly message boxes
- No external libraries required

## Requirements
For now, you need Windows 8 or newer as it is the minimum requirement to run YT-DLP. For Linux users, check the [roadmap](#roadmap).<br><br>
More importantly, you will also need a [YT-DLP](https://github.com/yt-dlp/yt-dlp) binary.<br><br>

If you plan on using the source code version, you must install the [latest Python version](https://www.python.org/downloads/). 🐍

## Using the Source Code

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Guilherme-A-Garcia/Easy-DLP.git
    cd Easy-DLP
    ```

2.  **Create and activate a virtual environment** (recommended):

    *   **Linux/macOS:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   **Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install the required packages** using the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

## How to Use
1. Download the latest release of this project;
2. Execute the .exe binary (or activate your virtual environment and run `python main.py` within the project directory);
3. Paste your YT-DLP file path in the "YT-DLP Path Directory Cache" window. For example, "C:/Users/YourName/Downloads/" if your YT-DLP binary is located in the 'Downloads' folder;
4. If you wish to download an age-restricted video from YouTube, log into your YouTube account and select your browser in the drop-down menu, clicking save after the process. Leave the selector at "None" if you don't need cookie importation;
5. Insert the URL of the video you're going to download and press "Download".

>[!TIP]
> You are able to clear the YT-DLP file path you provided by clicking "Clear path", doing this will close the application,<br>
  and will generate a new cache file once you open it up again.<br>
> If you are importing cookies, it MIGHT be preferable to close your browser before downloading any video.

## Roadmap
- ✅ Refactor to use classes instead of functions;
- ✅ Migrate to CustomTkinter;
- ✅ Themes;
- ✅ Additional path verification for better integrity;
- ❌ Add threading and a progress bar;
- ❌ Linux support;
- ❌ Playlist support;
- ❌ Add a settings tab;
- ❌ Add an auto-update system.
- ❌ Step up the game to PySide6;

## Contributing
✨ Contributions are always welcome! ✨<br><br>

### How to Contribute:
*   **Report Bugs**: Open an issue with detailed steps to reproduce.
*   **Suggest Features**: Open an issue to discuss your idea.
*   **Contribute Directly to the Code**:<br>
    I. Fork the repository;<br>
    II. Create a new branch;<br>
    III. Make your changes and commit;<br>
    IV. Push to the branch;<br>
    V. Open a Pull Request;<br>
    VI. Kindly wait for approval. ;)<br>
<br>
Thank you for reading!
