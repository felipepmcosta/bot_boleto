import psycopg2, logging

# Configurando o sistema de logging para o módulo db.py
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def inserir_token(mat, token):
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="BOLETOS",
            user="postgres",
            password="postgres",
            host="192.168.1.163"
        )
        cursor = conn.cursor()
        cursor.execute("UPDATE boletim_geral SET token = %s WHERE mat = %s", (token, mat))
        conn.commit()
    except psycopg2.Error as e:
        logger.error("Erro ao inserir token no PostgreSQL: %s", e)
    finally:
        if conn is not None:
            conn.close()

def atualizar_envio(mat):
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="BOLETOS",
            user="postgres",
            password="postgres",
            host="192.168.1.163"
        )
        cursor = conn.cursor()
        cursor.execute("UPDATE boletim_geral SET envio = now() WHERE mat = %s", (mat,))
        conn.commit()
    except psycopg2.Error as e:
        logger.error("Erro ao atualizar coluna 'envio' no PostgreSQL: %s", e)
    finally:
        if conn is not None:
            conn.close()

def extrair_emails(campos_email):
    emails = []
    for campo in campos_email:
        if campo:
            emails.extend(campo.split(','))
            
    return [email.strip() for email in emails if email.strip()]

def pega_contatos_db(mat_prefix=None, avaliacao_prefix=None):
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

        if mat_prefix is not None and avaliacao_prefix is not None:
            cursor.execute("SELECT mat, nom, avaliacao, boletim, token, email, data_gerado FROM boletim_geral WHERE LEFT(mat, 2) = %s AND avaliacao = %s AND envio IS NULL", (mat_prefix, avaliacao_prefix))
        else:
            cursor.execute("SELECT mat, nom, avaliacao, boletim, token, email, data_gerado FROM boletim_geral WHERE envio IS NULL")

        rows = cursor.fetchall()

        for row in rows:
            mat = row[0]
            nome = row[1]
            avaliacao = row[2]
            boletim = row[3]
            token = row[4]
            email = row[5]
            data_gerado = row[6]
            contatos.append({'mat': mat, 'nome': nome, 'avaliacao': avaliacao, 'boletim': boletim, 'token': token, 'email': email, 'data_gerado': data_gerado})
    except psycopg2.Error as e:
        logger.error("Erro ao conectar ao PostgreSQL: %s", e)
    finally:
        if conn is not None:
            conn.close()

    return contatos

def pega_contatos_teste(mat_prefix=None, avaliacao_prefix=None):
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

        if mat_prefix is not None and avaliacao_prefix is not None:
            cursor.execute("SELECT mat, nom, avaliacao, boletim, token, email, data_gerado FROM boletim_geral WHERE LEFT(mat, 2) = %s AND avaliacao = %s AND envio IS NULL", (mat_prefix, avaliacao_prefix))
        else:
            cursor.execute("SELECT mat, nom, avaliacao, boletim, token, email, data_gerado FROM boletim_geral WHERE envio IS NULL")

        rows = cursor.fetchall()

        for row in rows:
            mat = row[0]
            nome = row[1]
            avaliacao = row[2]
            boletim = row[3]
            token = row[4]
            email = row[5]
            data_gerado = row[6]
            contatos.append({'mat': mat, 'nome': nome, 'avaliacao': avaliacao, 'boletim': boletim, 'token': token, 'email': email, 'data_gerado': data_gerado})
    except psycopg2.Error as e:
        logger.error("Erro ao conectar ao PostgreSQL: %s", e)
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

    return contatos
