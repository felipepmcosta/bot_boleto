import psycopg2, logging

# Configurando o sistema de logging para o módulo db.py
logging.basicConfig(level=logging.INFO)
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

def atualizarEnvio(mat):
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="BOLETOS",
            user="postgres",
            password="postgres",
            host="192.168.1.163"
        )
        cursor = conn.cursor()
        cursor.execute("UPDATE boletos_geral SET envio = now() WHERE mat = %s", (mat,))
        conn.commit()
    except psycopg2.Error as e:
        logger.error("Erro ao atualizar coluna 'envio' no PostgreSQL: %s", e)
    finally:
        if conn is not None:
            conn.close()

def extrairEmails(camposEmail):
    emails = []
    for campo in camposEmail:
        if campo:
            emails.extend(campo.split(','))
            
    return [email.strip() for email in emails if email.strip()]

def pegaContatosDB(mat_prefix=None, cot_prefix=None):
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

        if mat_prefix is not None and cot_prefix is not None:
            cursor.execute("SELECT mat, nome, cot, boleto, digitavel, created_at, email FROM boletos_geral WHERE LEFT(mat, 2) = %s AND cot = %s AND envio IS NULL LIMIT 10", (mat_prefix, cot_prefix))
        else:
            cursor.execute("SELECT mat, nome, cot, boleto, digitavel, created_at, email FROM boletos_geral WHERE envio IS NULL LIMIT 10")

        rows = cursor.fetchall()

        for row in rows:
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


def pegaContatosTeste(mat_prefix=None, cot_prefix=None):
    contatos = []
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(
            dbname="BOLETOS",
            user="postgres",
            password="postgres",
            host="192.168.1.163"
        )
        cursor = conn.cursor()

        if mat_prefix is not None and cot_prefix is not None:
            cursor.execute("SELECT mat, nome, cot, boleto, digitavel, created_at, email FROM boletos_geral WHERE LEFT(mat, 2) = %s AND cot = %s AND envio IS NULL LIMIT 10", (mat_prefix, cot_prefix))
        else:
            cursor.execute("SELECT mat, nome, cot, boleto, digitavel, created_at, email FROM boletos_geral WHERE envio IS NULL LIMIT 10")

        rows = cursor.fetchall()

        for row in rows:
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
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

    return contatos
