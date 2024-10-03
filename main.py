import logging
import datetime
import gspread
from google.oauth2.service_account import Credentials

# Gera um nome de arquivo com a data e hora atuais
log_filename = datetime.datetime.now().strftime('estoque_log_%Y-%m-%d_%H-%M-%S.txt')

# Configuração do logger
logging.basicConfig(
    filename=log_filename,  # Nome do arquivo inclui a data e hora
    level=logging.INFO,      # Nível de log
    format='%(asctime)s - %(levelname)s - %(message)s'  # Formato da mensagem de log
)

logging.info('Iniciando o processamento de baixa de estoque.')

# Autenticação com a API Google usando gspread
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
gc = gspread.authorize(creds)

# IDs das planilhas (obter da URL)
ESTOQUE_SHEET_ID = '1B-jXS2Pexjj5YiaEWtOVUYRHd0djbo4Zru33juch9BU'
BAIXA_SHEET_ID = '1B-jXS2Pexjj5YiaEWtOVUYRHd0djbo4Zru33juch9BU'
HISTORICO_SHEET_ID = '1B-jXS2Pexjj5YiaEWtOVUYRHd0djbo4Zru33juch9BU'

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
    print(cell, value)
    worksheet.update(cell, [[value]])  # Atualiza a célula, passando o valor dentro de uma lista

# Função para adicionar uma linha no final da planilha
def append_row_to_sheet(worksheet, row_data):
    """Função para adicionar uma linha ao final da planilha."""
    worksheet.append_row(row_data)

# Função para limpar os dados da planilha de Baixa de Estoque
def clear_sheet_data(worksheet):
    """Função para limpar os dados de uma planilha, exceto o cabeçalho."""
    worksheet.batch_clear(['A2:F'])  # Limpa as linhas de dados, mantendo o cabeçalho

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
        data_hora, responsavel, categoria_baixa, nome_baixa, quantidade_baixa, justificativa = baixa
        quantidade_baixa = int(quantidade_baixa)

        # Encontra o item correspondente no estoque
        for i, item in enumerate(estoque):
            categoria_estoque, nome_estoque, quantidade_estoque = item
            if categoria_estoque == categoria_baixa and nome_estoque == nome_baixa:
                nova_quantidade = int(quantidade_estoque) - quantidade_baixa
               

                if nova_quantidade < 0:
                    logging.error(f"Erro: Estoque insuficiente para {nome_baixa}.")
                    continue

                # Atualiza a quantidade no estoque
                update_sheet_cell(estoque_worksheet, f'C{i+2}', nova_quantidade)
                logging.info(f'Item {nome_baixa}: Quantidade retirada = {quantidade_baixa}, Nova quantidade = {nova_quantidade}.')

                # Adiciona ao histórico
                historico_entry = [data_hora, responsavel, categoria_baixa, nome_baixa, quantidade_baixa, justificativa]
                append_row_to_sheet(historico_worksheet, historico_entry)
                break
        else:
            logging.error(f"Item {nome_baixa} não encontrado no estoque.")

    # Limpa os dados processados da planilha de Baixa
    clear_sheet_data(baixa_worksheet)
    logging.info('Processamento de baixa de estoque concluído com sucesso.')

# Chama a função principal
processar_baixa_estoque()
