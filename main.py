from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import logging
import datetime

# Gera um nome de arquivo com a data e hora atuais
log_filename = datetime.datetime.now().strftime('estoque_log_%Y-%m-%d_%H-%M-%S.txt')

# Configuração do logger
logging.basicConfig(
    filename=log_filename,  # Nome do arquivo inclui a data e hora
    level=logging.INFO,      # Nível de log
    format='%(asctime)s - %(levelname)s - %(message)s'  # Formato da mensagem de log
)

logging.info('Iniciando o processamento de baixa de estoque.')

# Autenticação com a API Google
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

# IDs das planilhas (obter da URL)
ESTOQUE_SHEET_ID = '1B-jXS2Pexjj5YiaEWtOVUYRHd0djbo4Zru33juch9BU'
BAIXA_SHEET_ID = '16QeIGkiog4RuxtETDpAVz6MTLM44KMVW86uID-he4Ow'
HISTORICO_SHEET_ID = '10KeAt9gf1NU2bHwFcxzCChonwdT5sA8FK919hLq9oSE'

def get_sheet_data(sheet_id, range_name, skip_header=True):
    """Função para pegar os dados de uma planilha, com opção de ignorar o cabeçalho."""
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
    data = result.get('values', [])
    
    # Se `skip_header` for True, retorna os dados a partir da segunda linha (sem o cabeçalho)
    if skip_header and len(data) > 1:
        return data[1:]  # Ignora a primeira linha (índice 0)
    else:
        return data

def update_sheet_data(sheet_id, range_name, values):
    """Função para atualizar dados em uma planilha."""
    body = {'values': values}
    result = service.spreadsheets().values().update(
        spreadsheetId=sheet_id, range=range_name,
        valueInputOption='RAW', body=body).execute()
    return result

def processar_baixa_estoque():
    # Pega os dados da planilha de Baixa de Estoque
    baixas = get_sheet_data(BAIXA_SHEET_ID, 'A:F')  # Exemplo: Baixas na planilha 2
    estoque = get_sheet_data(ESTOQUE_SHEET_ID, 'A:C')  # Exemplo: Estoque na planilha 1

    print(baixas)
    print(estoque)
    
    for baixa in baixas:  # Pulando a linha de cabeçalho
        data_hora, responsavel, categoria_baixa, nome_baixa, quantidade_baixa, justificativa = baixa
        quantidade_baixa = int(quantidade_baixa)

        # Encontra o item correspondente no estoque (mesma categoria e nome)
        for i, item in enumerate(estoque):  # Pulando cabeçalho e mantendo o índice correto
            categoria_estoque, nome_estoque, quantidade_estoque = item
            if categoria_estoque == categoria_baixa and nome_estoque == nome_baixa:
                nova_quantidade = int(quantidade_estoque) - quantidade_baixa
                logging.info(f'Item {item}: Quantidade retirada = {quantidade_baixa}, Nova quantidade = {nova_quantidade}.')

                if nova_quantidade < 0:
                    print(f"Erro: Estoque insuficiente para {nome_baixa}.")
                    continue

                # Atualiza o estoque
                estoque[i + 2][2] = str(nova_quantidade)  # Atualiza a quantidade
                update_sheet_data(ESTOQUE_SHEET_ID, f'C{i + 2}', [[nova_quantidade]])

                # Atualiza o histórico
                historico_entry = [data_hora, responsavel, categoria_baixa, nome_baixa, quantidade_baixa, justificativa]
                update_sheet_data(HISTORICO_SHEET_ID, f'A:F', [historico_entry])
                break
        else:
            print(f"Item {nome_baixa} não encontrado no estoque.")


    # Remove as baixas já processadas da planilha de Baixa
    update_sheet_data(BAIXA_SHEET_ID, 'A:F', [[''] * 6] * (len(baixas) - 1))

    logging.info('Processamento de baixa de estoque concluído com sucesso.')

processar_baixa_estoque()