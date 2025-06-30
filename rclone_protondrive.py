import subprocess  # noqa: S404
from pathlib import Path

RESYNC_MESSAGE = "ERROR : Bisync aborted. Must run --resync to recover."
LOCK_MESSAGE = "NOTICE: Failed to bisync: prior lock file found: "
LOG_DIR = "/home/truls/rclone-logs/"

BASE_COMMAND = "rclone bisync "
SYNC_ALL = "protondrive: /home/truls/Documents "
SYNC_2025 = "protondrive:2025 /home/truls/Documents/2025 "
OPTIONS = r"-v --force --min-size 1b --max-lock 90m "
RESYNC = "--resync "
LOG = r"--log-file=/home/truls/rclone-logs/protondrive-$(date +\%Y\%m\%d\%H\%M).log"
LOG_RESYNC = r"--log-file=/home/truls/rclone-logs/protondrive-$(date +\%Y\%m\%d\%H\%M)_resync.log"


def main():
    log_file_name = get_last_log_file()

    resync = check_log(log_file_name, RESYNC_MESSAGE)
    if resync:
        rename_log_file(log_file_name, "resync-to-recover")

    lock = check_log(log_file_name, LOCK_MESSAGE)
    if lock:
        rename_log_file(log_file_name, "lock-file-found")

    if resync:
        command = BASE_COMMAND + SYNC_ALL + OPTIONS + RESYNC + LOG_RESYNC
        print("Resync message found in log file. Running resync command...")
        return_code, _stdout, _stderr = run_command(command)
    else:
        command = BASE_COMMAND + SYNC_ALL + OPTIONS + LOG
        print("No resync message found in log file. Running normal command...")
        return_code, _stdout, _stderr = run_command(command)

    if return_code != 0:
        print("Command failed with return code:", return_code)


def get_last_log_file():
    log_files = [f for f in Path(LOG_DIR).iterdir() if f.name.startswith("protondrive-") and f.name.endswith(".log")]
    if not log_files:
        return None
    log_files.sort(reverse=True)
    return Path(LOG_DIR) / log_files[0]


def check_log(log_file_path, message):
    try:
        print(f"Checking log file: {log_file_path}, for message: {message}")
        with Path(log_file_path).open(encoding="utf-8") as log_file:
            for line in log_file:
                if message in line:
                    return True
    except FileNotFoundError:
        print(f"Log file {log_file_path} not found.")
    return False


def rename_log_file(log_file_path, tag):
    if log_file_path:
        new_log_file_name = log_file_path.with_name(f"{log_file_path.stem}_{tag}.log")
        log_file_path.rename(new_log_file_name)
        print(f"Renamed log file to: {new_log_file_name}")


def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # noqa: S602
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr


if __name__ == "__main__":
    main()
