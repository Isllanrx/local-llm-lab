import sys
import platform
import subprocess
from datetime import datetime
from src.config.settings import LOGS_DIR

def is_windows() -> bool:
    return platform.system() == "Windows"

def get_current_time() -> str:
    return datetime.now().strftime("%H:%M")

def write_log(filename: str, message: str):
    try:
        log_path = LOGS_DIR / f"{filename}.txt"
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"{message}\n")
    except Exception as e:
        print(f"Erro ao escrever no log: {e}")

def run_command(command: list, creationflags: int = 0) -> str:
    return subprocess.check_output(
        command,
        text=True,
        encoding='utf-8',
        creationflags=creationflags
    )
