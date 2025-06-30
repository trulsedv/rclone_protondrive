import argparse
import subprocess  # noqa: S404
from pathlib import Path

RESYNC_MESSAGE = "ERROR : Bisync aborted. Must run --resync to recover."
LOCK_MESSAGE = "NOTICE: Failed to bisync: prior lock file found: "
LOG_DIR = "/home/truls/rclone-logs/"

SYNC_CHOICES = ["SYNC_ALL", "SYNC_2025"]

BASE_COMMAND = "rclone bisync "
SYNC_ALL = "protondrive: /home/truls/Documents "
SYNC_2025 = "protondrive:2025 /home/truls/Documents/2025 "
OPTIONS = "-v --force --min-size 1b --max-lock 90m "
RESYNC = "--resync "
LOG = r"--log-file=/home/truls/rclone-logs/protondrive-$(date +\%Y\%m\%d\%H\%M).log"
LOG_RESYNC = r"--log-file=/home/truls/rclone-logs/protondrive-$(date +\%Y\%m\%d\%H\%M)_resync.log"


def main(args):
    if args.sync_type == "SYNC_2025":  # noqa: SIM108
        sync_type = SYNC_2025
    else:
        sync_type = SYNC_ALL

    log_file_name = get_last_log_file()

    resync = check_log(log_file_name, RESYNC_MESSAGE)
    if resync:
        log_file_name = rename_log_file(log_file_name, "resync-to-recover")

    lock = check_log(log_file_name, LOCK_MESSAGE)
    if lock:
        log_file_name = rename_log_file(log_file_name, "lock-file-found")

    if resync:
        command = BASE_COMMAND + sync_type + OPTIONS + RESYNC + LOG_RESYNC
        print("Resync message found in log file. Running resync command: ", command)
        return_code, _stdout, _stderr = run_command(command)
    else:
        command = BASE_COMMAND + sync_type + OPTIONS + LOG
        print("Running rclone command: ", command)
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
        with Path(log_file_path).open(encoding="utf-8") as log_file:
            for line in log_file:
                if message in line:
                    print(f"Found message '{message}' in log file.")
                    return True
    except FileNotFoundError:
        print(f"Log file {log_file_path} not found.")
    return False


def rename_log_file(log_file_path, tag):
    new_log_file_name = log_file_path.with_name(f"{log_file_path.stem}_{tag}.log")
    log_file_path.rename(new_log_file_name)
    print(f"Renamed log file to: {new_log_file_name}")
    return new_log_file_name


def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # noqa: S602
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr


def parse_arguments():
    parser = argparse.ArgumentParser(description="Run rclone bisync with specified sync type.")
    parser.add_argument("--sync-type", type=str, choices=SYNC_CHOICES, help="Specify the sync type")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
