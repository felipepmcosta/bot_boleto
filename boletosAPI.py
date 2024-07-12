# enviarBoletos.py
import os
import sys
import smtplib
import logging
import datetime
import json
import requests
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
    mat_prefix = sys.argv[1]
    cot_prefix = sys.argv[2]

# Função para ler o modelo do e-mail a ser enviado
def lerTemplate(filename):
    with open(filename, 'r', encoding='utf-8') as arquivotemplate:
        return Template(arquivotemplate.read())

# Função para enviar e-mail usando a API
def enviarEmailAPI(para, de, assunto, texto, html, api_url):
    try:
        data = {
            "para": para,
            "de": de,
            "assunto": assunto,
            "texto": texto,
            "html": html
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(api_url, headers=headers, json=data)

        if response.status_code == 200:
            logging.info(f'E-mail enviado usando API para {para}')
            return True
        else:
            logging.error(f'Falha ao enviar e-mail usando API para {para}. Status code: {response.status_code}')
            return False

    except requests.exceptions.RequestException as e:
        logging.error(f'Erro ao enviar e-mail usando API: {str(e)}')
        return False

if __name__ == '__main__':
    # Parâmetros para filtrar os contatos
    mat_prefix = None
    cot_prefix = None

    # Carregar dados do arquivo JSON
    with open('teste.json', 'r', encoding='utf-8') as json_file:
        dados_json = json.load(json_file)

    # Ler o conteúdo do arquivo msg.html e substituir variáveis
    with open('msg.html', 'r', encoding='utf-8') as html_file:
        template_html = html_file.read()

    # Substituir variáveis no HTML com dados do JSON
    template_html = template_html.replace('${PERSON_NAME}', 'Nome da Pessoa')
    template_html = template_html.replace('${LINK}', 'http://192.168.1.214:3355/sendEmail')

    # Atualizar o JSON com o conteúdo HTML substituído
    dados_json['html'] = template_html

    # Executar o envio de e-mail usando a API
    enviado = enviarEmailAPI(
        dados_json['para'],
        dados_json['de'],
        dados_json['assunto'],
        dados_json['texto'],
        dados_json['html'],
        'http://192.168.1.214:3355/sendEmail'
    )

    if enviado:
        print('E-mail enviado com sucesso!')
    else:
        print('Falha ao enviar o e-mail.')
