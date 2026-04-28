import psycopg2
import psycopg2.pool
import logging
from email_validator import validate_email, EmailNotValidError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_DB_PARAMS = dict(
    dbname="BOLETOS",
    user="postgres",
    password="postgres",
    host="192.168.1.163"
)

_pool = psycopg2.pool.SimpleConnectionPool(minconn=1, maxconn=5, **_DB_PARAMS)


def atualizar_envio(mat, conn=None):
    _own_conn = conn is None
    if _own_conn:
        conn = _pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE boletos_geral SET envio = now() WHERE mat = %s", (mat,))
        conn.commit()
        cursor.close()
    except psycopg2.Error as e:
        logger.error("Erro ao atualizar coluna 'envio' no PostgreSQL: %s", e)
    finally:
        if _own_conn:
            _pool.putconn(conn)


def extrair_emails(campos_email):
    emails = []
    for campo in campos_email:
        if campo:
            emails.extend(campo.split(','))
    valid_emails = []
    for email in emails:
        email = email.strip()
        if email:
            try:
                v = validate_email(email, check_deliverability=False)
                valid_emails.append(v.email)
            except EmailNotValidError as e:
                logger.error(f"E-mail inválido descartado: {email} - {str(e)}")
    return list(set(valid_emails))


def inserir_log_boletos(mat, cot, destinatario, conn=None):
    _own_conn = conn is None
    if _own_conn:
        conn = _pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO log_boletos (mat, cot, destinatario, data_tentativa)
            VALUES (%s, %s, %s, NOW())
            """,
            (mat, cot, destinatario)
        )
        conn.commit()
        cursor.close()
        logger.info(f"Log inserido para mat: {mat}, cot: {cot}, destinatario: {destinatario}")
    except psycopg2.Error as e:
        logger.error(f"Erro ao registrar log de envio na tabela log_boletos: {str(e)}")
    finally:
        if _own_conn:
            _pool.putconn(conn)


def pega_contatos_db(mat_prefix=None, cot_prefix=None):
    conn = _pool.getconn()
    try:
        # named cursor = server-side, busca em batches sem carregar tudo na RAM
        cursor = conn.cursor('cursor_envio_boletos')
        cursor.itersize = 500

        if mat_prefix is not None and cot_prefix is not None:
            cursor.execute(
                """
                SELECT nome, mat, cot, token, geracao, email
                FROM boletos_geral
                WHERE mat = %s
                AND LEFT(mat, 2) = %s
                AND cot = %s
                AND envio IS NULL
                AND token IS NOT NULL
                AND AGE(now(), geracao) < INTERVAL '28 days'
                ORDER BY mat
                """,
                (mat_prefix, mat_prefix[:2], cot_prefix)
            )
        else:
            cursor.execute(
                """
                SELECT nome, mat, cot, token, geracao, email
                FROM boletos_geral
                WHERE envio IS NULL
                AND token IS NOT NULL
                AND AGE(now(), geracao) < INTERVAL '28 days'
                ORDER BY mat
                """
            )

        for row in cursor:
            yield {
                'nome': row[0],
                'mat': row[1],
                'cot': row[2],
                'token': row[3],
                'geracao': row[4],
                'email': row[5],
            }

        cursor.close()
    except psycopg2.Error as e:
        logger.error("Erro ao conectar ao PostgreSQL: %s", e)
    finally:
        _pool.putconn(conn)
