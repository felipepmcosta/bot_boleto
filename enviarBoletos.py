# enviaBoletos.py
import os, sys
import smtplib
import logging
import datetime
import json
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email_validator import validate_email
from db import Database

# Configurando o sistema de logging
logging.basicConfig(filename='email_logs.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Verificando os argumentos mat_prefix e cot_prefix
if len(sys.argv) < 3:
    print("Os argumentos 'mat_prefix' e 'cot_prefix' não foram fornecidos. Enviando boletos para todos os contatos disponíveis...")
    mat_prefix = None
    cot_prefix = None
else:
    # Atribuindo os argumentos a 'mat_prefix' e 'cot_prefix'
    mat_prefix = sys.argv[1]
    cot_prefix = sys.argv[2]

# Constantes para configurações de e-mail
SMTP_HOST = 'smtp.smce.rio.br'
SMTP_PORT = 8025
SMTP_USERNAME = 'boleto@smce.rio.br'
SMTP_PASSWORD = 'EchH464%'

# Constante para o remetente padrão
EMAIL_SENDER = 'boleto@smce.rio.br'

# Variável de controle para pausar o envio de e-mails
envioPausado = False

link = "https://boletos.santamonicarede.com.br/"

def lerTemplate(filename):
    # Função para ler o modelo do e-mail a ser enviado
    with open(filename, 'r', encoding='utf-8') as arquivotemplate:
        return Template(arquivotemplate.read())

def pegaUnidade(matricula):
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
    destinatario_temporario = "maycon.csc@smrede.com.br"
    try:
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

def registro_xml(envios, tipo_relatorio, data_hora):
    try:
        # Obtendo a data e hora para incluir no título do arquivo
        data = data_hora.split()[0]  # Obtém apenas a parte da data
        hora = data_hora.split()[1]  # Obtém apenas a parte da hora

        # Construindo o nome do arquivo com base na data e hora atuais
        nome_arquivo = f"relatorio_envios_{data}_{hora}.xml"

        # Criando o arquivo XML de relatório
        with open(nome_arquivo, 'w') as arquivo_xml:
            arquivo_xml.write("<?xml version='1.0' encoding='UTF-8'?>\n")
            arquivo_xml.write("<relatorio>\n")
            for envio in envios:
                arquivo_xml.write("  <envio>\n")
                arquivo_xml.write(f"    <matricula>{envio['matricula']}</matricula>\n")
                arquivo_xml.write(f"    <nome>{envio['nome']}</nome>\n")
                arquivo_xml.write(f"    <destinatario>{envio['destinatario']}</destinatario>\n")
                arquivo_xml.write(f"    <data_hora>{envio['data_hora']}</data_hora>\n")
                arquivo_xml.write(f"    <status>{tipo_relatorio}</status>\n")
                arquivo_xml.write("  </envio>\n")
            arquivo_xml.write("</relatorio>\n")

        logging.info(f'Arquivo XML de relatório "{nome_arquivo}" criado com sucesso.')
    except Exception as ex:
        logging.error(f'Ocorreu um erro ao gerar o arquivo XML de relatório: {ex}')

def enviar_boletos(mat_prefix, cot_prefix):
    try:
        contatos = Database().pega_contatos_db(mat_prefix, cot_prefix)
        for contato in contatos:
            if envioPausado:
                logging.info('Envio de e-mails pausado.')
                break
            nome = contato['nome']
            mat = contato['mat']
            cot = contato['cot']
            unidade = pegaUnidade(mat)
            email = contato['email']
            emailsUnidade = emailsPorUnidade().get(unidade, [])
            mensagem_template = lerTemplate('msg.html')
            mensagem = mensagem_template.substitute(PERSON_NAME=nome.title(), LINK=f"{link}{contato['token']}")
            assunto = f"Seu BOLETO SMREDE - Unidade {unidade} chegou!!!"
            enviado = enviarEmail(email, assunto, mensagem, emailsUnidade)
            if enviado:
                Database().atualizar_envio(mat)
            else:
                logging.error(f"Falha ao enviar e-mail para {nome} ({email})")
    except Exception as ex:
        logging.error(f"Ocorreu um erro ao enviar os boletos: {ex}")

if __name__ == '__main__':
    # Parâmetros para filtrar os contatos
    mat_prefix = None
    cot_prefix = None

    # Executando a função para enviar boletos
    enviar_boletos(mat_prefix, cot_prefix)
