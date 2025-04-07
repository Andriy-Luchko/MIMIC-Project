import os
import sys
import shutil
import tempfile
import psutil

MARKER_FILENAME = ".my_app_pid"

def get_temp_mei_folders():
    """Find all _MEIxxxxxx folders in the system temp directory."""
    temp_dir = tempfile.gettempdir()
    return [os.path.join(temp_dir, d) for d in os.listdir(temp_dir) if d.startswith("_MEI")]

def is_pid_running(pid):
    """Check if a given PID is still running."""
    try:
        return psutil.pid_exists(pid) and psutil.Process(pid).name() == sys.argv[0]
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

def cleanup_old_mei_folders():
    current_mei = getattr(sys, '_MEIPASS', None)

    for folder in get_temp_mei_folders():
        if folder == current_mei:
            continue  # Never delete our own MEI folder

        marker_path = os.path.join(folder, MARKER_FILENAME)
        
        if os.path.exists(marker_path):
            try:
                with open(marker_path, "r") as f:
                    pid = int(f.read().strip())

                if not is_pid_running(pid):
                    shutil.rmtree(folder)
                    print(f"Removed stale MEI folder: {folder}")
            except Exception as e:
                print(f"Failed to check or remove {folder}: {e}")

def write_marker_file():
    """Write a marker file with the current PID in our MEI folder."""
    current_mei_folder = getattr(sys, '_MEIPASS', None)
    if current_mei_folder:
        try:
            marker_path = os.path.join(current_mei_folder, MARKER_FILENAME)
            with open(marker_path, "w") as f:
                f.write(str(os.getpid()))
        except Exception as e:
            print(f"Failed to write marker file: {e}")

def mei_lifecycle():
    cleanup_old_mei_folders()
    write_marker_file()
# def main():
#     cleanup_old_mei_folders()  # Clean up old folders on startup
#     write_marker_file()  # Mark our current MEI folder

# if __name__ == "__main__":
#     main()
