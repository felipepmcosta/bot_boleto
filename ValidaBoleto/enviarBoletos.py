import os, smtplib, logging, hashlib, datetime, re, traceback, sys, requests
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email_validator import validate_email, EmailNotValidError
from db import pega_contatos_db, atualizar_envio

# Obtendo os argumentos da linha de comando
args = sys.argv[1:]  # Ignora o primeiro argumento, que é o nome do script

# Verificando se foram fornecidos argumentos suficientes
if len(args) < 2:
    print("Os argumentos 'mat_prefix' e 'cot_prefix' não foram fornecidos. Enviando boletos para todos os contatos disponíveis...")
    mat_prefix = None
    cot_prefix = None
else:
    # Atribuindo os argumentos a 'mat_prefix' e 'cot_prefix'
    mat_prefix = args[0]
    cot_prefix = args[1]

# Obtendo os contatos com base nos dois primeiros dígitos de 'mat' e 'cot' da função pegaContatosDB()
contatos = pega_contatos_db(mat_prefix, cot_prefix)

# Se não houver contatos disponíveis, exiba uma mensagem e saia
if not contatos:
    print("Não foram encontrados contatos para enviar boletos. Todos já foram enviados.")
    sys.exit(1)

# Constante para o remetente padrão
EMAIL_SENDER = 'boleto@smrede.com.br'

# Variável de controle para pausar o envio de e-mails
envio_pausado = False

# Configuração do sistema de logging
logging.basicConfig(filename='email_logs.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Link do Boleto
link = "https://boletos.santamonicarede.com.br/"  

def ler_template(filename):
    # Função para ler o modelo do e-mail a ser enviado
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, filename)
    with open(file_path, 'r', encoding='utf-8') as arquivotemplate:
        return Template(arquivotemplate.read())

def pega_unidade(matricula):
    # Função para obter a unidade com base na matrícula
    unidades = {
        "01": "Bento Ribeiro",
        "02": "Madureira",
        "03": "Santa Cruz",
        "04": "Cascadura",
        "05": "Taquara",
        "06": "Nilópolis",
        "09": "Seropédica",
        "10": "Barra da Tijuca",
        "11": "Campo Grande",
        "13": "Mangueira",
        "14": "Maricá",
        "15": "Ilha do Governador",
        "16": "Freguesia",
        "17": "Recreio dos Bandeirantes"
    }
    numero = matricula[:2]
    return unidades.get(numero, "Sem Unidade selecionada")

def obter_mes_ano(cot):
    meses = {
        "01": "Janeiro",
        "02": "Fevereiro",
        "03": "Março",
        "04": "Abril",
        "05": "Maio",
        "06": "Junho",
        "07": "Julho",
        "08": "Agosto",
        "09": "Setembro",
        "10": "Outubro",
        "11": "Novembro",
        "12": "Dezembro"
    }
    mes_numero = cot.zfill(2)  # Garante que o número do mês tenha dois dígitos (ex.: "1" → "01")
    mes_nome = meses.get(mes_numero, "Mês Desconhecido")
    ano = datetime.datetime.now().year
    return f"{mes_nome}/{ano}"

def enviarEmail(destinatario, assunto, mensagem, mat):
    destinatario_temporario = "marcos.csc@smrede.com.br"
    
    try:
        envio_destinatarios = list(set([email.strip() for email in destinatario.split(',') if email.strip()]))

        for destinatario_individual in envio_destinatarios:
            try:
                # Validação de e-mail
                v = validate_email(destinatario_individual)
                email_validado = v.email  # Acessando o e-mail validado corretamente
            except EmailNotValidError as e:
                raise ValueError(f"O email '{destinatario_individual}' não está em um formato válido: {str(e)}")

            # Obter a unidade com base na matrícula
            unidade = pega_unidade(mat)

            # Dados do JSON incorporados no código
            dados_json = {
                "para": destinatario_individual,  # Usando cada destinatário individualmente
                "de": EMAIL_SENDER,  # Certifique-se de definir EMAIL_SENDER com seu endereço de e-mail
                "assunto": assunto,
                "html": mensagem,  # Conteúdo HTML do e-mail
                "categorias": ["Boleto", unidade]
            }

            # URL da API para enviar e-mail
            api_url = 'https://sendmail.smrede.tec.br/sendEmail'

            # Executar o envio de e-mail usando a API
            enviado = sendMessage(dados_json, api_url)

            if enviado:
                logging.info(f'E-mail enviado para {destinatario_individual} usando API.')
            else:
                logging.error(f'Falha ao enviar e-mail para {destinatario_individual} usando API.')

        return True  # Indica que todos os e-mails foram enviados com sucesso

    except (requests.exceptions.RequestException, ValueError) as e:
        logging.error(f'Erro ao enviar o e-mail: {str(e)}')
        return False

def sendMessage(dados_json, api_url):
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(api_url, headers=headers, json=dados_json)

        if response.status_code == 200:
            logging.info(f'E-mail enviado usando API para {dados_json["para"]}')
            return True
        else:
            logging.error(f'Falha ao enviar e-mail usando API para {dados_json["para"]}. Status code: {response.status_code}')
            return False 

    except requests.exceptions.RequestException as e:
        logging.error(f'Erro ao enviar e-mail usando API: {str(e)}')
        return False

try:
    contatos = pega_contatos_db(mat_prefix, cot_prefix)
    mensagem_template = ler_template('msg.html')
    envio_corretos = []
    envio_incorretos = []
    for contato in contatos:
        if envio_pausado:
            logging.info('Envio de e-mails pausado.')
            break
        nome = contato['nome']
        mat = contato['mat']
        unidade = pega_unidade(mat)
        email = contato['email']
        token = contato['token']
        linkToken = f"{link}{token}"
        mensagem = mensagem_template.substitute(PERSON_NAME=nome.title(), LINK=linkToken, MES_ANO=obter_mes_ano(contato['cot']), UNIDADE=unidade)
        assunto = f"Seu BOLETO SMREDE - Unidade {unidade} chegou!!!"
        enviado = enviarEmail(email, assunto, mensagem, mat)
        if enviado:
            envio_corretos.append({'data_hora': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 'destinatario': email, 'nome': nome, 'matricula': mat, 'unidade': unidade})
            atualizar_envio(mat)
        else:
            if email not in [envio['destinatario'] for envio in envio_incorretos]:
                envio_incorretos.append({'destinatario': email, 'nome': nome, 'matricula': mat, 'email': email, 'data_hora': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 'unidade': unidade})

except Exception as ex:
    logging.error('Ocorreu um erro ao enviar e-mails: %s', ex)