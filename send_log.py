import os
import telebot
from credentials import BOT_TOKEN, GROUP_ID

# Inicializa o bot
bot = telebot.TeleBot(BOT_TOKEN)

# Função para encontrar o último arquivo de log na pasta Logs
def get_latest_log(log_dir='logs'):
    try:
        files = [os.path.join(log_dir, f) for f in os.listdir(log_dir) if os.path.isfile(os.path.join(log_dir, f))]
        files.sort(key=os.path.getmtime, reverse=True)
        return files[0] if files else None
    except Exception as e:
        print(f"Erro ao acessar a pasta Logs: {e}")
        return None

# Função para ler o conteúdo do último arquivo de log
def read_log_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"Erro ao ler o arquivo de log: {e}")
        return None

# Função principal para enviar o log ao grupo
def send_log_to_group():
    log_file = get_latest_log()
    if not log_file:
        print("Nenhum arquivo de log encontrado.")
        return

    log_content = read_log_file(log_file)
    if not log_content:
        print("O arquivo de log está vazio ou não pôde ser lido.")
        return

    try:
        bot.send_message(GROUP_ID, f"{log_content}")
        print(f"Log enviado com sucesso via Telegram.")
    except Exception as e:
        print(f"Erro ao enviar mensagem para o grupo: {e}")

# Torna a função importável sem executar automaticamente
if __name__ == "__main__":
    send_log_to_group()