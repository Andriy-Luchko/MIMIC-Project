import os
import sys
import zipfile
import subprocess
import psutil
import time
import errno

def wait_for_app_to_close(app_path):
    print("[Updater] Waiting for app to exit...")
    app_pid = os.getppid()  # get parent PID (the app that launched us)
    try:
        p = psutil.Process(app_pid)
        p.wait(timeout=30)
        return True
    except Exception:
        return False

def wait_until_file_unlocked(path, timeout=30):

    for _ in range(timeout * 2):
        try:
            if os.name == "nt":
                os.rename(path, path)
            else:
                with open(path, "a"):
                    pass
            return True
        except OSError as e:
            if e.errno in [errno.EACCES, errno.EPERM]:
                time.sleep(0.5)
            else:
                raise
    return False

def main():
    if len(sys.argv) != 3:
        print("Usage: updater.py <zip_path> <app_path>")
        return

    zip_path, app_path = sys.argv[1], sys.argv[2]
    app_dir = os.path.dirname(app_path)

    wait_for_app_to_close(app_path)
    wait_until_file_unlocked(app_path)

    print("[Updater] Extracting update...")
    with zipfile.ZipFile(zip_path, "r") as z:
        for member in z.namelist():
            filename = os.path.join(app_dir, member)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "wb") as f:
                f.write(z.read(member))

    os.remove(zip_path)
    print("[Updater] Relaunching app...")
    subprocess.Popen([app_path], close_fds=True)
    sys.exit(0)
