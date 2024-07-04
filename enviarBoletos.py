import os, smtplib, logging, hashlib, datetime, re, traceback
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email_validator import validate_email, EmailNotValidError
from db import pegaContatosDB, inserirToken, pegaContatosTeste, atualizarEnvio
import sys

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
contatos = pegaContatosTeste(mat_prefix, cot_prefix)

# Se não houver contatos disponíveis, exiba uma mensagem e saia
if not contatos:
    print("Não foram encontrados contatos para enviar boletos. Todos já foram enviados.")
    sys.exit(1)


# Constantes para configurações de e-mail
SMTP_HOST = 'smtp.smce.rio.br'
SMTP_PORT = 8025
SMTP_USERNAME = 'boleto@smce.rio.br'
SMTP_PASSWORD = 'EchH464%'

# Constante para o remetente padrão
EMAIL_SENDER = 'boleto@smce.rio.br'

# Variável de controle para pausar o envio de e-mails
envioPausado = False

# Configuração do sistema de logging
logging.basicConfig(filename='email_logs.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

link = "https://boletos.santamonicarede.com.br/"

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
        "Bento Ribeiro": ["maycon.csc@smrede.com.br", "boleto@smce.rio.br"],
        "Madureira": ["maycon.csc@smrede.com.br", "boleto@smce.rio.br"],
        "Santa Cruz": ["maycon.csc@smrede.com.br", "boleto@smce.rio.br"],
        "Cascadura": ["maycon.csc@smrede.com.br", "boleto@smce.rio.br"],
        "Taquara": ["maycon.csc@smrede.com.br", "boleto@smce.rio.br"],
        "Nilópolis": ["maycon.csc@smrede.com.br", "boleto@smce.rio.br"],
        "Seropédica": ["maycon.csc@smrede.com.br", "boleto@smce.rio.br"],
        "Barra da Tijuca": ["maycon.csc@smrede.com.br", "boleto@smce.rio.br"],
        "Campo Grande": ["maycon.csc@smrede.com.br", "boleto@smce.rio.br"],
        "Mangueira": ["maycon.csc@smrede.com.br", "boleto@smce.rio.br"],
        "Maricá": ["maycon.csc@smrede.com.br", "boleto@smce.rio.br"],
        "Ilha do Governador": ["maycon.csc@smrede.com.br", "boleto@smce.rio.br"],
        "Freguesia": ["maycon.csc@smrede.com.br", "boleto@smce.rio.br"],
        "Recreio dos Bandeirantes": ["maycon.csc@smrede.com.br", "boleto@smce.rio.br"]
    }
    return emailsUnidade

def enviarEmail(destinatario, assunto, mensagem, emailsUnidade=None):
    try:
        destinatario_temporario = "maycon.csc@smrede.com.br"
        # Dividindo vários endereços de e-mail e removendo strings vazias
        destinatarios = [email.strip() for email in destinatario.split(',') if email.strip()]
        for destinatario in destinatarios:
            if not validate_email(destinatario):
                raise ValueError(f"O email '{destinatario}' não está em um formato válido.")
        s = smtplib.SMTP(host=SMTP_HOST, port=SMTP_PORT)
        s.starttls()
        s.login(SMTP_USERNAME, SMTP_PASSWORD)
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = destinatario_temporario
        if emailsUnidade:
            msg['Cc'] = ", ".join(emailsUnidade)  # Adiciona os emails da unidade como cópia
        msg['Subject'] = assunto
        msg.attach(MIMEText(mensagem, 'html'))
        s.send_message(msg)
        s.quit()
        return True

    except (smtplib.SMTPAuthenticationError, smtplib.SMTPException, ValueError) as e:
        logging.error(f'Erro ao enviar o e-mail: {str(e)}')
        return False

def relatorio_por_unidade(envios, tipo_relatorio, destinatario_temporario):
    try:
        envios_por_unidade = {}
        for envio in envios:
            unidade = envio.get('unidade', 'Outros')
            if unidade not in envios_por_unidade:
                envios_por_unidade[unidade] = {'sucesso': [], 'problema': []}
            if tipo_relatorio == "Sucesso":
                envios_por_unidade[unidade]['sucesso'].append(envio)
            elif tipo_relatorio == "Problema":
                envios_por_unidade[unidade]['problema'].append(envio)

        # Criando relatório por unidade
        for unidade, envios_unidade in envios_por_unidade.items():
            data_hora_atual = datetime.datetime.now()
            total_sucesso = len(envios_unidade['sucesso'])
            total_problema = len(envios_unidade['problema'])
            corpo_email = f"""\
<html>
    <head></head>
    <body>
        <p>Relatório de Envios - Unidade {unidade}</p>
        <p>Data do Relatório: {data_hora_atual.strftime("%d/%m/%Y")}</p>
        <p>Hora do Relatório: {data_hora_atual.strftime("%H:%M:%S")}</p>
        <p>Total de Envios com Sucesso: {total_sucesso}</p>
        <p>Total de Envios com Problema: {total_problema}</p>
"""
            # Adicionar tabela apenas se houver envios com problema
            if total_problema > 0:
                corpo_email += """\
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
                for idx, envio in enumerate(envios_unidade['problema'], start=1):
                    corpo_email += f"""\
            <tr style='background-color: #ffeac4;'>
                <td>{idx}</td>
                <td>{envio['matricula']}</td>
                <td>{envio['nome']}</td>
                <td>{envio['destinatario']}</td>
                <td>{envio['data_hora']}</td>
                <td>Problema</td>
            </tr>
"""
                corpo_email += """\
        </table>
"""
            corpo_email += """\
    </body>
</html>
"""
            assunto = f"Relatório de Envios - Unidade {unidade}"
            enviado = enviarEmail(destinatario_temporario, assunto, corpo_email)  # Aqui passamos a mensagem como argumento
            if enviado:
                logging.info(f'Relatório de envios para a unidade {unidade} enviado por e-mail.')
            else:
                logging.error(f'Falha ao enviar o relatório de envios para a unidade {unidade} por e-mail.')
    except Exception as ex:
        logging.error(f'Ocorreu um erro ao gerar os relatórios de envio de e-mail por unidade: {ex}')


try:
    contatos = pegaContatosDB(mat_prefix, cot_prefix)
    envio_corretos = []
    envio_incorretos = []
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
        mensagem_template = lerTemplate('msg.html')
        mensagem = mensagem_template.substitute(PERSON_NAME=nome.title(), LINK=linkToken)
        assunto = f"Seu BOLETO SMREDE - Unidade {unidade} chegou!!!"
        enviado = enviarEmail(email, assunto, mensagem)
        if enviado:
            envio_corretos.append({'data_hora': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 'destinatario': email, 'nome': nome, 'matricula': mat, 'unidade': unidade})
            atualizarEnvio(mat)
        else:
            if email not in [envio['destinatario'] for envio in envio_incorretos]:
                envio_incorretos.append({'destinatario': email, 'nome': nome, 'matricula': mat, 'email': email, 'data_hora': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 'unidade': unidade})
    relatorio_por_unidade(envio_corretos, "Sucesso", destinatario_temporario="maycon.csc@smrede.com.br")
    relatorio_por_unidade(envio_incorretos, "Problema", destinatario_temporario="maycon.csc@smrede.com.br")

except Exception as ex:
    logging.error('Ocorreu um erro ao gerar os relatórios de envio de e-mail: %s', ex)

def registro_xml(envios, tipo_relatorio, data_hora):
    try:
        # Obtendo a data e hora para incluir no título do arquivo
        data = data_hora.split()[0]  # Obtém apenas a parte da data
        hora = data_hora.split()[1]  # Obtém apenas a parte da hora
        data_formatada = data.replace("/", "-")  # Substitui "/" por "-" para evitar problemas com nomes de arquivos
        hora_formatada = hora.replace(":", ".")  # Substitui ":" por "." para evitar problemas com nomes de arquivos

        # Compondo o nome do arquivo com o tipo de relatório, data e hora
        nome_arquivo = f"{tipo_relatorio}_{data_formatada}_{hora_formatada}.xml"

        # Diretório onde o arquivo será salvo (pode ser ajustado conforme necessário)
        diretorio = "relatorioBoleto_xml"

        # Verificando se o diretório existe, caso contrário, criando-o
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)

        # Caminho completo para o arquivo
        caminho_arquivo = os.path.join(diretorio, nome_arquivo)

        with open(caminho_arquivo, "w", encoding="utf-8") as file:
            for envio in envios:
                line = ", ".join([f"{key}: {value}" for key, value in envio.items()])
                file.write(line + "\n")

    except Exception as ex:
        # Em caso de erro, registra no arquivo XML
        logging.error(f'Ocorreu um erro ao gerar o relatório XML: {ex}')
        with open(caminho_arquivo, "w", encoding="utf-8") as file:
            file.write(f'Ocorreu um erro ao gerar o relatório XML: {ex}')

try:
    contatos = pegaContatosDB(mat_prefix, cot_prefix)
    mensagem_template = lerTemplate('msg.html')
    envio_corretos = []
    envio_incorretos = []
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
        mensagem = mensagem_template.substitute(PERSON_NAME=nome.title(), LINK=linkToken)
        assunto = f"Seu BOLETO SMREDE - Unidade {unidade} chegou!!!"
        enviado = enviarEmail(email, assunto, mensagem)
        if enviado:
            envio_corretos.append({'data_hora': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 'destinatario': email, 'nome': nome, 'matricula': mat, 'unidade': unidade})

        else:
            if email not in [envio['destinatario'] for envio in envio_incorretos]:
                envio_incorretos.append({'destinatario': email, 'nome': nome, 'matricula': mat, 'email': email, 'data_hora': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 'unidade': unidade, 'erro': 'Erro ao enviar o e-mail: An email address cannot have a period immediately after the @-sign.'})

    relatorio_por_unidade(envio_corretos, "Sucesso", destinatario_temporario="maycon.csc@smrede.com.br")
    relatorio_por_unidade(envio_incorretos, "Problema", destinatario_temporario="maycon.csc@smrede.com.br")

    # Obtendo a data e hora atual
    data_hora_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    # Registrando envios corretos em um arquivo XML
    logging.info('Registrando envios corretos em XML...')
    registro_xml(envio_corretos, "relatorioSucesso", data_hora_atual)
    logging.info('Envios corretos registrados em XML.')
    # Registrando envios incorretos em um arquivo XML
    logging.info('Registrando envios incorretos em XML...')
    registro_xml(envio_incorretos, "relatorioProblema", data_hora_atual)
    logging.info('Envios incorretos registrados em XML.')
except Exception as ex:
    logging.error('Ocorreu um erro ao gerar o relatório de e-mail: %s', ex)
