import logging
import datetime
import os
import gspread
from google.oauth2.service_account import Credentials
from send_log import send_log_to_group
from credentials import ESTOQUE_SHEET_ID, BAIXA_SHEET_ID, HISTORICO_SHEET_ID

# Gera um nome de arquivo com a data e hora atuais
log_filename = datetime.datetime.now().strftime('estoque_log_%Y-%m-%d_%H-%M-%S.txt')

# Cria a pasta Logs, caso não exista
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Caminho completo do arquivo de log
log_filepath = os.path.join(log_dir, log_filename)

# Configuração do logger
logging.basicConfig(
    filename=log_filepath,  # Salva o arquivo na pasta Logs
    level=logging.INFO,      # Nível de log
    format='%(message)s'  # Formato da mensagem de log
)

logging.info('Started')

# Autenticação com a API Google usando gspread
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file('chaveDeAcesso-GoogleCloud.json', scopes=SCOPES)
gc = gspread.authorize(creds)

# Função para acessar uma planilha específica por ID e aba
def get_worksheet(sheet_id, sheet_name):
    """Função para acessar uma aba específica de uma planilha."""
    spreadsheet = gc.open_by_key(sheet_id)
    return spreadsheet.worksheet(sheet_name)

# Função para ler dados de uma planilha, ignorando linhas vazias e opcionalmente o cabeçalho
def get_sheet_data(worksheet, skip_header=True):
    """Função para pegar os dados de uma planilha, ignorando o cabeçalho e linhas vazias."""
    data = worksheet.get_all_values()

    # Se `skip_header` for True, ignora a primeira linha (cabeçalho)
    if skip_header:
        data = data[1:]

    # Filtra as linhas vazias
    data = [row for row in data if any(cell.strip() for cell in row)]

    return data

# Função para atualizar uma célula específica
def update_sheet_cell(worksheet, cell, value):
    """Função para atualizar uma célula específica em uma planilha."""
    worksheet.update(cell, [[value]])  # Atualiza a célula, passando o valor dentro de uma lista

# Função para adicionar uma linha no final da planilha
def append_row_to_sheet(worksheet, row_data):
    """Função para adicionar uma linha ao final da planilha."""
    worksheet.append_row(row_data)

# Função para limpar os dados da planilha de Baixa de Estoque
def clear_sheet_data(worksheet):
    """Função para limpar os dados de uma planilha, exceto o cabeçalho."""
    worksheet.batch_clear(['A2:E'])  # Limpa as linhas de dados, mantendo o cabeçalho

# Função principal de processamento de baixa de estoque
def processar_baixa_estoque():
    # Acessa as planilhas
    baixa_worksheet = get_worksheet(BAIXA_SHEET_ID, 'Baixa de Estoque')
    estoque_worksheet = get_worksheet(ESTOQUE_SHEET_ID, 'Estoque')
    historico_worksheet = get_worksheet(HISTORICO_SHEET_ID, 'Histórico')

    # Pega os dados da planilha de Baixa de Estoque e do Estoque
    baixas = get_sheet_data(baixa_worksheet)  # Exemplo: Baixas na planilha 2
    estoque = get_sheet_data(estoque_worksheet)  # Exemplo: Estoque na planilha 1

    for baixa in baixas:
        data_hora, responsavel, nome_baixa, quantidade_baixa, justificativa = baixa
        quantidade_baixa = int(quantidade_baixa)

        # Encontra o item correspondente no estoque
        for i, item in enumerate(estoque):
            nome_estoque, quantidade_estoque = item
            if nome_estoque == nome_baixa:
                nova_quantidade = int(quantidade_estoque) - quantidade_baixa

                if nova_quantidade < 0:
                    logging.error(f"Erro: Estoque insuficiente para {nome_baixa}.")
                    continue

                # Atualiza a quantidade no estoque
                update_sheet_cell(estoque_worksheet, f'B{i+2}', nova_quantidade)
                logging.info(f'• O item "{nome_baixa}" teve {quantidade_baixa} unidade(s) retirada(s). Quantidade atual: {nova_quantidade}.')

                # Adiciona ao histórico
                historico_entry = [data_hora, responsavel, nome_baixa, quantidade_baixa, justificativa]
                append_row_to_sheet(historico_worksheet, historico_entry)
                break
        else:
            logging.error(f"Item {nome_baixa} não encontrado no estoque.")

    # Limpa os dados processados da planilha de Baixa
    clear_sheet_data(baixa_worksheet)
    logging.info('Completed')

# Chama a função principal
processar_baixa_estoque()
send_log_to_group()