import os
import sys
import threading
import requests
import logging
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

GITHUB_API = "https://api.github.com/repos/Andriy-Luchko/MIMIC-Project/releases/latest"

def get_real_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.argv[0])
    else:
        return os.path.dirname(os.path.abspath(__file__))

# ✅ THEN set up logging
log_file = os.path.join(get_real_app_dir(), "update.log")
logging.basicConfig(
    filename=log_file,
    filemode="a",
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.DEBUG
)
print(f"[Logger] Writing logs to: {log_file}")

class UpdateChecker(QObject):
    update_available = pyqtSignal(str)  # emits download_url

    def __init__(self):
        super().__init__()
        self.local_version = self._get_local_version()
        logging.debug(f"Local version is: {self.local_version}")

    def _get_local_version(self):
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(__file__)

            version_path = os.path.join(base_path, "version.txt")
            with open(version_path, "r") as f:
                version = f.read().strip()
                logging.debug(f"Read version from {version_path}: {version}")
                return version
        except Exception as e:
            logging.error(f"Failed to read version.txt: {e}")
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
                logging.info("Checking for update...")
                response = requests.get(GITHUB_API, timeout=5)
                release = response.json()
                latest_version = release["tag_name"].lstrip("v")
                logging.info(f"Latest GitHub version: {latest_version}")

                if latest_version != self.local_version:
                    logging.info("Update available.")
                    platform = self._get_platform_tag()
                    for asset in release["assets"]:
                        if platform in asset["name"].lower():
                            url = asset["browser_download_url"]
                            logging.info(f"Update URL found: {url}")
                            self.update_available.emit(url)
                            break
                    else:
                        logging.warning("No matching platform asset found in release.")
                else:
                    logging.info("Application is up to date.")
            except Exception as e:
                logging.error(f"Error during update check: {e}")

        threading.Thread(target=run, daemon=True).start()

    def apply_update(self, url):
        try:
            from PyQt5.QtWidgets import QMessageBox
            import subprocess

            app_path = os.path.abspath(sys.executable)
            app_dir = os.path.dirname(app_path)
            zip_path = os.path.join(app_dir, "update.zip")
            updater_path = os.path.join(app_dir, "updater.py")

            logging.info(f"App path: {app_path}")
            logging.info(f"Update zip will be saved to: {zip_path}")
            logging.info(f"Updater path: {updater_path}")

            QMessageBox.information(
                None,
                "Updating...",
                "The app will now update and restart."
            )

            logging.info("Starting download...")
            r = requests.get(url, stream=True)
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            logging.info("Download complete.")

            logging.info("Launching updater...")
            subprocess.Popen(
                [sys.executable, updater_path, zip_path, app_path],
                close_fds=True
            )

            logging.info("Exiting main application to allow update...")
            sys.exit(0)

        except Exception as e:
            logging.error(f"Updater failed: {e}")
