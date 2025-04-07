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
            app_dir = os.path.dirname(sys.executable)
            zip_path = os.path.join(app_dir, "update.zip")
            print(f"[Updater] Downloading update from: {url}")
            print(f"[Updater] Will save to: {zip_path}")

            # Download the update
            r = requests.get(url, stream=True)
            total_size = int(r.headers.get('Content-Length', 0))
            print(f"[Updater] Total download size: {total_size / 1024:.2f} KB")

            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"[Updater] Download complete. Verifying...")

            if not os.path.exists(zip_path) or os.path.getsize(zip_path) == 0:
                print("[Updater] ERROR: Downloaded file is missing or empty!")
                return

            # Extract to temp
            extract_dir = os.path.join(app_dir, "update_extract")
            os.makedirs(extract_dir, exist_ok=True)
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(extract_dir)

            print(f"[Updater] Extracted files to: {extract_dir}")
            if os.path.exists(os.path.join(extract_dir, "version.txt")):
                with open(os.path.join(extract_dir, "version.txt")) as f:
                    print(f"[Updater] Extracted version.txt says: {f.read().strip()}")
            else:
                print("[Updater] WARNING: version.txt not found in zip!")

            # Replace app files
            for item in os.listdir(extract_dir):
                src = os.path.join(extract_dir, item)
                dst = os.path.join(app_dir, item)

                print(f"[Updater] Replacing: {dst}")
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)

            shutil.rmtree(extract_dir)
            os.remove(zip_path)

            print("[Updater] Update complete. Restarting app...")
            os.execl(sys.argv[0], sys.argv[0])


        except Exception as e:
            print(f"[Updater] ERROR: {e}")

