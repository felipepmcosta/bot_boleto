import os, smtplib, logging, hashlib, traceback, datetime, re
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email_validator import validate_email, EmailNotValidError
from db import pegaContatosDB, inserirToken, pegaContatosTeste

# Constantes para configurações de e-mail
SMTP_HOST = 'smtp.smce.rio.br'
SMTP_PORT = 8025
SMTP_USERNAME = 'boleto@smce.rio.br'
SMTP_PASSWORD = 'EchH464%'

# Constante para o remetente padrão
EMAIL_SENDER = 'boleto@smce.rio.br'

# Constante para o endereço de resposta padrão
EMAIL_REPLY_TO = 'maycon.csc@smrede.com.br'

# Variável de controle para pausar o envio de e-mails
envioPausado = False

# Configuração do sistema de logging
logging.basicConfig(filename='email_logs.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

link = "http://192.168.1.214:3333/valida_boleto/"

def gerarToken(cot, mat):
    # Concatenar os dados em uma única string
    dadosConcatenados = f"{cot}{mat}"
    
    # Calcular o hash MD5 da string concatenada com o link
    hash_md5 = hashlib.md5((dadosConcatenados).encode()).hexdigest()
    
    return hash_md5

def lerTemplate(filename):
    # function para ler o modelo do e-mail a ser enviado
    with open(filename, 'r', encoding='utf-8') as arquivotemplate:
        return Template(arquivotemplate.read())

def pegaUnidade(matricula):
    # function para obter a unidade com base na matrícula
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
    return unidades.get(numero, "Matriz")

def emailsPorUnidade():
    # Dicionário mapeando cada unidade para seus emails correspondentes
    emailsUnidade = {
        "Bento Ribeiro": ["yoshichaolan@gmail.com", "mayconcartoon@gmail.com"],
        "Madureira": ["yoshichaolan@gmail.com", "mayconcartoon@gmail.com"],
        "Santa Cruz": ["yoshichaolan@gmail.com", "mayconcartoon@gmail.com"],
        "Cascadura": ["yoshichaolan@gmail.com", "mayconcartoon@gmail.com"],
        "Taquara": ["yoshichaolan@gmail.com", "mayconcartoon@gmail.com"],
        "Nilópolis": ["yoshichaolan@gmail.com", "mayconcartoon@gmail.com"],
        "Seropédica": ["yoshichaolan@gmail.com", "mayconcartoon@gmail.com"],
        "Barra da Tijuca": ["yoshichaolan@gmail.com", "mayconcartoon@gmail.com"],
        "Campo Grande": ["yoshichaolan@gmail.com", "mayconcartoon@gmail.com"],
        "Mangueira": ["yoshichaolan@gmail.com", "mayconcartoon@gmail.com"],
        "Maricá": ["yoshichaolan@gmail.com", "mayconcartoon@gmail.com"],
        "Ilha do Governador": ["yoshichaolan@gmail.com", "mayconcartoon@gmail.com"],
        "Freguesia": ["yoshichaolan@gmail.com", "mayconcartoon@gmail.com"],
        "Recreio dos Bandeirantes": ["yoshichaolan@gmail.com", "mayconcartoon@gmail.com"]
    }
    return emailsUnidade

def enviarEmail(destinatario, assunto, mensagem, emailsUnidade=None):
    try:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", destinatario):
            raise ValueError(f"O email '{destinatario}' não está em um formato válido.")
        if not validate_email(destinatario):
            raise ValueError(f"O domínio do email '{destinatario}' não é válido.")
        s = smtplib.SMTP(host=SMTP_HOST, port=SMTP_PORT)
        s.starttls()
        s.login(SMTP_USERNAME, SMTP_PASSWORD)
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = destinatario
        if emailsUnidade:
            msg['Cc'] = ", ".join(emailsUnidade)  # Adiciona os emails da unidade como cópia
        msg['Reply-to'] = EMAIL_REPLY_TO
        msg['Subject'] = assunto
        msg.attach(MIMEText(mensagem, 'html'))
        s.send_message(msg)
        s.quit()
        return True
    
    except (smtplib.SMTPAuthenticationError, smtplib.SMTPException, ValueError) as e:
        logging.error(f'Erro ao enviar o e-mail: {str(e)}')
        return False

def relatorioPorUnidade(envios, tipoRelatorio):
    try:
        enviosPorUnidade = {}
        for envio in envios:
            unidade = envio.get('unidade', 'Outros')
            if unidade not in enviosPorUnidade:
                enviosPorUnidade[unidade] = {'sucesso': [], 'problema': []}
            if tipoRelatorio == "Sucesso":
                enviosPorUnidade[unidade]['sucesso'].append(envio)
            elif tipoRelatorio == "Problema":
                enviosPorUnidade[unidade]['problema'].append(envio)

        # Criando relatório por unidade
        for unidade, enviosUnidade in enviosPorUnidade.items():
            dataHoraAtual = datetime.datetime.now()
            total_sucesso = len(enviosUnidade['sucesso'])
            total_problema = len(enviosUnidade['problema'])
            corpoEmail = f"""\
<html>
    <head></head>
    <body>
        <p>Relatório de Envios - Unidade {unidade}</p>
        <p>Data do Relatório: {dataHoraAtual.strftime("%d/%m/%Y")}</p>
        <p>Hora do Relatório: {dataHoraAtual.strftime("%H:%M:%S")}</p>
        <p>Total de Envios com Sucesso: {total_sucesso}</p>
        <p>Total de Envios com Problema: {total_problema}</p>
"""
            # Adicionar tabela apenas se houver envios com problema
            if total_problema > 0:
                corpoEmail += """\
        <p>Aqui estão os detalhes dos envios com problema:</p>
        <table border='1' cellpadding='5' style='border-collapse: collapse; text-align: center;'>
            <tr style='background-color: #120a8f; color: white;'>
                <th>Quantidade</th>
                <th>Matrícula</th>
                <th>Nome</th>
                <th>Email</th>
                <th>Data de Envio</th>
                <th>Status</th>
"""
                for idx, envio in enumerate(enviosUnidade['problema'], start=1):
                    corpoEmail += f"""\
            <tr style='background-color: #ffeac4;'>
                <td>{idx}</td>
                <td>{envio['matricula']}</td>
                <td>{envio['nome']}</td>
                <td>{envio['destinatario']}</td>
                <td>{envio['dataHora']}</td>
                <td>Problema</td>
            </tr>
"""
                corpoEmail += """\
        </table>
"""
            corpoEmail += """\
    </body>
</html>
"""
            assunto = f"Relatório de Envios - Unidade {unidade}"
            enviado = enviarEmail(EMAIL_REPLY_TO, assunto, corpoEmail)
            if enviado:
                logging.info(f'Relatório de envios para a unidade {unidade} enviado por e-mail.')
            else:
                logging.error(f'Falha ao enviar o relatório de envios para a unidade {unidade} por e-mail.')
    except Exception as ex:
        logging.error(f'Ocorreu um erro ao gerar os relatórios de envio de e-mail por unidade: {ex}')

try:
    contatos = pegaContatosTeste()
    enviosCorretos = []
    enviosIncorretos = []
    for contato in contatos:
        if envioPausado:
            logging.info('Envio de e-mails pausado.')
            break
        nome = contato['nome']
        mat = contato['mat']
        cot = contato['cot']
        unidade = pegaUnidade(mat)
        email = contato['email']
        token = gerarToken(cot, mat)
        inserirToken(mat, token)
        linkToken = f"{link}{token}"
        mensagemTemplate = lerTemplate('msg.html')
        mensagem = mensagemTemplate.substitute(PERSON_NAME=nome.title(), LINK=linkToken)
        assunto = f"Seu BOLETO SMREDE - Unidade {unidade} chegou!!!"
        enviado = enviarEmail(email, assunto, mensagem)
        if enviado:
            enviosCorretos.append({'dataHora': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 'destinatario': email, 'nome': nome, 'matricula': mat, 'unidade': unidade})
        else:
            if email not in [envio['destinatario'] for envio in enviosIncorretos]:
                enviosIncorretos.append({'destinatario': email, 'nome': nome, 'matricula': mat, 'email': email, 'dataHora': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 'unidade': unidade})
    relatorioPorUnidade(enviosCorretos, "Sucesso")
    relatorioPorUnidade(enviosIncorretos, "Problema")
except Exception as ex:
    logging.error('Ocorreu um erro ao gerar os relatórios de envio de e-mail: %s', ex)


def registroXml(envios, tipoRelatorio, dataHora):
    try:
        # Obtendo a data e hora para incluir no título do arquivo
        data = dataHora.split()[0]  # Obtém apenas a parte da data
        hora = dataHora.split()[1]  # Obtém apenas a parte da hora
        dataFormatada = data.replace("/", "-")  # Substitui "/" por "-" para evitar problemas com nomes de arquivos
        horaFormatada = hora.replace(":", ".") # Substitui ":" por "." para evitar problemas com nomes de arquivos

        # Compondo o nome do arquivo com o tipo de relatório, data e hora
        nomeArquivo = f"{tipoRelatorio}_{dataFormatada}_{horaFormatada}.xml"

        # Diretório onde o arquivo será salvo (pode ser ajustado conforme necessário)
        diretorio = "relatorioBoleto_xml"

        # Verificando se o diretório existe, caso contrário, criando-o
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)

        # Caminho completo para o arquivo
        caminhoArquivo = os.path.join(diretorio, nomeArquivo)

        with open(caminhoArquivo, "w", encoding="utf-8") as file:
            for envio in envios:
                line = ", ".join([f"{key}: {value}" for key, value in envio.items()])
                file.write(line + "\n")

    except Exception as ex:
        # Em caso de erro, registra no arquivo XML
        logging.error(f'Ocorreu um erro ao gerar o relatório XML: {ex}')
        with open(caminhoArquivo, "w", encoding="utf-8") as file:
            file.write(f'Ocorreu um erro ao gerar o relatório XML: {ex}')


try:
    contatos = pegaContatosTeste()
    mensagemTemplate = lerTemplate('msg.html')
    enviosCorretos = []
    enviosIncorretos = []
    for contato in contatos:
        if envioPausado:
            logging.info('Envio de e-mails pausado.')
            break
        nome = contato['nome']
        mat = contato['mat']
        cot = contato['cot']
        unidade = pegaUnidade(mat)
        email = contato['email']
        token = gerarToken(cot, mat)
        inserirToken(mat, token)
        linkToken = f"{link}{token}"
        mensagem = mensagemTemplate.substitute(PERSON_NAME=nome.title(), LINK=linkToken)
        assunto = f"Seu BOLETO SMREDE - Unidade {unidade} chegou!!!"
        enviado = enviarEmail(email, assunto, mensagem)
        if enviado:
            enviosCorretos.append({'dataHora': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 'destinatario': email, 'nome': nome, 'matricula': mat, 'unidade': unidade})
        else:
            if email not in [envio['destinatario'] for envio in enviosIncorretos]:
                enviosIncorretos.append({'destinatario': email, 'nome': nome, 'matricula': mat, 'email': email, 'dataHora': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 'unidade': unidade, 'erro': 'Erro ao enviar o e-mail: An email address cannot have a period immediately after the @-sign.'})
    
    relatorioPorUnidade(enviosCorretos, "Sucesso")
    relatorioPorUnidade(enviosIncorretos, "Problema")
    # Obtendo a data e hora atual
    dataHoraAtual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    # Registrando envios corretos em um arquivo XML
    logging.info('Registrando envios corretos em XML...')
    registroXml(enviosCorretos, "relatorioSucesso", dataHoraAtual)
    logging.info('Envios corretos registrados em XML.')
    # Registrando envios incorretos em um arquivo XML
    logging.info('Registrando envios incorretos em XML...')
    registroXml(enviosIncorretos, "relatorioProblema", dataHoraAtual)
    logging.info('Envios incorretos registrados em XML.')
except Exception as ex:
    logging.error('Ocorreu um erro ao gerar o relatório de e-mail: %s', ex)