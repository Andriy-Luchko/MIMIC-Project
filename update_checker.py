import os
import sys
import threading
import requests
import zipfile
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import shutil

GITHUB_API = "https://api.github.com/repos/Andriy-Luchko/MIMIC-Project/releases/latest"

def get_real_app_dir():
    # If bundled with PyInstaller, use parent of the .app or .exe
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.argv[0])
    else:
        # Running as raw script
        return os.path.dirname(os.path.abspath(__file__))

class UpdateChecker(QObject):
    update_available = pyqtSignal(str)  # emits download_url

    def __init__(self):
        super().__init__()
        self.local_version = self._get_local_version()

    def _get_local_version(self):
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(__file__)

            version_path = os.path.join(base_path, "version.txt")
            with open(version_path, "r") as f:
                return f.read().strip()
        except Exception as e:
            print(f"[UpdateChecker] Failed to read version.txt: {e}")
            return "0.0.0"


    def _get_platform_tag(self):
        if sys.platform.startswith("win"):
            return "windows"
        elif sys.platform.startswith("darwin"):
            return "macos"
        elif sys.platform.startswith("linux"):
            return "linux"
        return "unknown"

    def check_for_update(self):
        def run():
            try:
                response = requests.get(GITHUB_API, timeout=5)
                release = response.json()
                latest_version = release["tag_name"].lstrip("v")

                if latest_version != self.local_version:
                    platform = self._get_platform_tag()
                    for asset in release["assets"]:
                        if platform in asset["name"].lower():
                            self.update_available.emit(asset["browser_download_url"])
                            break
            except Exception as e:
                print(f"[UpdateChecker] Error: {e}")

        threading.Thread(target=run, daemon=True).start()

    def apply_update(self, url):
        try:
            from PyQt5.QtWidgets import QMessageBox
            import subprocess

            app_path = sys.argv[0]
            app_dir = os.path.dirname(app_path)
            zip_path = os.path.join(app_dir, "update.zip")

            # Show message while updating
            QMessageBox.information(
                None,
                "Updating...",
                "The app will now update and restart."
            )

            # Download update
            r = requests.get(url, stream=True)
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Launch updater in a new process
            updater_path = os.path.join(app_dir, "updater.py")
            subprocess.Popen(
                [sys.executable, updater_path, zip_path, app_path],
                close_fds=True
            )

            sys.exit(0)

        except Exception as e:
            print(f"[Updater] ERROR: {e}")
