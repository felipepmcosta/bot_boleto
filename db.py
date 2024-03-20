import psycopg2
import logging

# Configurando o sistema de logging para o módulo db.py
logger = logging.getLogger(__name__)

def inserirToken(mat, token):
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="BOLETOS",
            user="postgres",
            password="postgres",
            host="192.168.1.163"
        )
        cursor = conn.cursor()
        cursor.execute("UPDATE boletos_geral SET token = %s WHERE mat = %s", (token, mat))
        conn.commit()
    except psycopg2.Error as e:
        logger.error("Erro ao inserir token no PostgreSQL: %s", e)
    finally:
        if conn is not None:
            conn.close()

def extrairEmails(camposEmail):
    emails = []
    for campo in camposEmail:
        if campo:
            emails.extend(campo.split(','))
            
    return [email.strip() for email in emails if email.strip()]

def pegaContatosDB():
    contatos = []
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="BOLETOS",
            user="postgres",
            password="postgres",
            host="192.168.1.163"
        )
        cursor = conn.cursor()

        # Execute a consulta SQL para selecionar os dados necessários
        cursor.execute("SELECT mat, nome, cot, boleto, digitavel, created_at, email FROM boletos_geral")
        rows = cursor.fetchall()

        # Imprime os nomes das colunas retornadas pela consulta SQL
        colunas = [desc[0] for desc in cursor.description]
        logger.info("Colunas retornadas pela consulta SQL: %s", colunas)

        for row in rows:
            logger.debug("Linha retornada da consulta SQL: %s", row)
            mat = row[0]
            nome = row[1]
            cot = row[2]
            boleto = row[3]
            linha = row[4]
            dataGerado = row[5]
            email_str = row[6]
            emails = [email.strip() for email in email_str.split(',')]
            for email in emails:
                contatos.append({'mat': mat, 'nome': nome, 'cot': cot, 'boleto': boleto, 'linha': linha, 'dataGerado': dataGerado, 'email': email.strip()})
    except psycopg2.Error as e:
        logger.error("Erro ao conectar ao PostgreSQL: %s", e)
    finally:
        if conn is not None:
            conn.close()

    return contatos

def pegaContatosTeste():
    contatos = [
        {'mat': '011503098', 'nome': 'Teste', 'cot': '01','email': 'maycon.csc@smrede.com.br'},
        {'mat': '061515151', 'nome': 'Teste', 'cot': '01','email': 'mad@.com.br'},
        {'mat': '081954547', 'nome': 'Teste', 'cot': '01','email': 'maycon@gmailll.com'}
    ]

    return contatos






