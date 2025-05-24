import psycopg2
import logging
from email_validator import validate_email, EmailNotValidError

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def atualizar_envio(mat):
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
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

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

def pega_contatos_db(mat_prefix=None, cot_prefix=None):
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
            cursor.execute(
                """
                SELECT * FROM boletos_geral" 
                WHERE mat = %s
                AND LEFT(mat, 2) = %s 
                AND cot = %s
                AND envio is NULL 
                AND token is NOT NULL
                AND AGE(now(), geracao) < INTERVAL '28 days'
                ORDER BY mat
                """,
                (mat_prefix, mat_prefix[:2], cot_prefix)
            )
        else:
            cursor.execute(
                """
                SELECT * FROM boletos_geral 
                WHERE envio is NULL 
                AND token is NOT NULL
                AND AGE(now(), geracao) < INTERVAL '28 days'
                ORDER BY mat
                """
                )

        rows = cursor.fetchall()

        # Encontrar a data mais recente entre os resultados
        data_mais_recente = max(row[9] for row in rows) if rows else None

        # Iterar sobre os resultados e filtrar apenas os registros com a data mais recente
        for row in rows:
            id = row[0]
            mat = row[1]
            nome = row[2]
            cot = row[3]
            boleto = row[4]
            digitavel = row[5]
            token = row[6]
            envio = row[7]
            geracao = row[8]
            created_at = row[9]
            updated_at = row[10]
            email = row[11]
            cpfa = row[12]
            cpf = row[13]
            cpf2 = row[14]
            pix = row[15]

            # Verificar se a data gerada é a mais recente
            if created_at == data_mais_recente:
                contatos.append({
                    'id': id,
                    'mat': mat,
                    'nome': nome,
                    'cot': cot,
                    'boleto': boleto,
                    'digitavel': digitavel,
                    'token': token,
                    'envio': envio,
                    'geracao': geracao,
                    'created_at': created_at,
                    'updated_at': updated_at,
                    'email': email,
                    'cpfa': cpfa,
                    'cpf': cpf,
                    'cpf2': cpf2,
                    'pix': pix
                })
    
    except psycopg2.Error as e:
        logger.error("Erro ao conectar ao PostgreSQL: %s", e)
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

    return contatos