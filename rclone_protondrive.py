import subprocess  # noqa: S404
from pathlib import Path

NORMAL_COMMAND = r"rclone bisync ProtonDrive: /home/truls/Documents -v --force --min-size 1b --max-lock 90m --log-file=/home/truls/rclone-logs/protondrive-$(date +\%Y\%m\%d\%H\%M).log"
RESYNC_COMMAND = r"rclone bisync ProtonDrive: /home/truls/Documents -v --force --min-size 1b --max-lock 90m --log-file=/home/truls/rclone-logs/protondrive-$(date +\%Y\%m\%d\%H\%M)-resync.log --resync"
RESYNC_MESSAGE = "ERROR : Bisync aborted. Must run --resync to recover."
LOCK_MESSAGE = "NOTICE: Failed to bisync: prior lock file found: "
LOG_DIR = "/home/truls/rclone-logs/"


def main():
    log_file_name = get_last_log_file()

    if check_log(log_file_name, RESYNC_MESSAGE):
        print("Error found in log file. Running resync command...")
        return_code, _stdout, _stderr = run_command(RESYNC_COMMAND)
    else:
        print("No error found in log file. No resync needed. Running normal command...")
        return_code, _stdout, _stderr = run_command(NORMAL_COMMAND)

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
        print(f"Checking log file: {log_file_path}")
        with Path(log_file_path).open(encoding="utf-8") as log_file:
            for line in log_file:
                if message in line:
                    return True
    except FileNotFoundError:
        print(f"Log file {log_file_path} not found.")
    return False


def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # noqa: S602
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr


if __name__ == "__main__":
    main()
