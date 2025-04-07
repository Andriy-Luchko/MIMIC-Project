import os
import sys
import threading
import requests
import zipfile
import shutil
from PyQt5.QtWidgets import QMessageBox, QApplication

GITHUB_API = "https://api.github.com/repos/Andriy-Luchko/MIMIC-Project/releases/latest"

def get_local_version():
    try:
        with open(os.path.join(os.path.dirname(__file__), "version.txt")) as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"

def get_platform_tag():
    if sys.platform.startswith("win"):
        return "windows"
    elif sys.platform.startswith("darwin"):
        return "macos"
    elif sys.platform.startswith("linux"):
        return "linux"
    return "unknown"

def prompt_update(download_url, app_executable_path):
    app = QApplication(sys.argv)
    reply = QMessageBox.question(None, "Update Available",
                                 "A new version of MimicQuery is available. Would you like to update now?",
                                 QMessageBox.Yes | QMessageBox.No)

    if reply == QMessageBox.Yes:
        # Download the update zip
        try:
            r = requests.get(download_url, stream=True)
            zip_path = os.path.join(os.path.dirname(app_executable_path), "update.zip")
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Extract it
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.dirname(app_executable_path))

            os.remove(zip_path)
            QMessageBox.information(None, "Update Complete", "The app will now restart to apply the update.")
            os.execl(app_executable_path, app_executable_path)

        except Exception as e:
            QMessageBox.critical(None, "Update Failed", f"Could not apply update:\n{e}")

def check_for_update():
    try:
        local_version = get_local_version()
        response = requests.get(GITHUB_API, timeout=5)
        release = response.json()
        latest_version = release["tag_name"].lstrip("v")

        if latest_version != local_version:
            platform = get_platform_tag()
            for asset in release["assets"]:
                if platform in asset["name"].lower():
                    prompt_update(asset["browser_download_url"], sys.executable)
                    break
    except Exception as e:
        print(f"[Update Check] Failed: {e}")

def run_update_check_in_background():
    threading.Thread(target=check_for_update, daemon=True).start()
