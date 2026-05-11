import subprocess
import sys
import os
import ctypes
from typing import List
from src.utils.helpers import is_windows, run_command

class OllamaClient:
    def __init__(self):
        self._check_installed()

    def _check_installed(self):
        try:
            cmd = ["ollama", "--version"]
            subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Erro: Ollama não está instalado ou não está no PATH.")
            sys.exit(1)

    def get_models(self) -> List[str]:
        try:
            if is_windows():
                output = run_command(
                    ["powershell", "-Command", "ollama list"],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                output = run_command(["ollama", "list"])

            lines = output.strip().split("\n")[1:]
            return [line.split()[0] for line in lines if line]
        except Exception as e:
            print(f"Erro ao obter modelos: {e}")
            return []

    def chat(self, model: str, prompt: str) -> str:
        model_safe = model.replace("'", "''")
        if is_windows():
            command = ["powershell", "-Command", f"ollama run '{model_safe}' '{prompt}'"]
            return run_command(command, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            command = ["ollama", "run", model, prompt]
            return run_command(command)

def ensure_admin():
    if is_windows():
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)
    else:
        if os.geteuid() != 0:
            print("Este script precisa ser executado como root.")
            sys.exit(1)
