import os
import schedule
import time
import subprocess

# Caminho para o Python no ambiente virtual
VENV_PYTHON = os.path.join(".venv", "Scripts", "python.exe")

# Caminho para o script main.py
MAIN_SCRIPT_PATH = "main.py"

def run_main_script():
    try:
        print("Executando o script main.py...")
        subprocess.run([VENV_PYTHON, MAIN_SCRIPT_PATH], check=True)
        print("Script executado com sucesso.")
    except Exception as e:
        print(f"Erro ao executar o script: {e}")

# Agendamento
schedule.every().day.at("09:00").do(run_main_script)
schedule.every().day.at("17:00").do(run_main_script)

print("Agendador iniciado. Aguardando horários para executar o script...")

while True:
    schedule.run_pending()
    time.sleep(1)