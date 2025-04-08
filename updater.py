import os
import sys
import zipfile
import subprocess
import psutil

def wait_for_app_to_close(app_path):
    print("[Updater] Waiting for app to exit...")
    for proc in psutil.process_iter(attrs=['exe']):
        if proc.info['exe'] and app_path in proc.info['exe']:
            try:
                proc.wait(timeout=20)
            except psutil.TimeoutExpired:
                print("[Updater] Timed out waiting for app to close.")
                return False
    return True

def main():
    if len(sys.argv) != 3:
        print("Usage: updater.py <zip_path> <app_path>")
        return

    zip_path, app_path = sys.argv[1], sys.argv[2]
    app_dir = os.path.dirname(app_path)

    if not wait_for_app_to_close(app_path):
        print("[Updater] App didn't close in time.")
        return

    print("[Updater] Extracting update...")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(app_dir)

    os.remove(zip_path)
    print("[Updater] Relaunching app...")
    subprocess.Popen([app_path])
    sys.exit(0)

if __name__ == "__main__":
    main()
