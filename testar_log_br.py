import psycopg2
import logging
from email_validator import validate_email, EmailNotValidError

# Configuração de logging
logging.basicConfig(filename='test_log_todas_unidades.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Lista de unidades com seus prefixos
UNIDADES = {
    "01": "Bento Ribeiro",
    "02": "Madureira",
    "03": "Santa Cruz",
    "04": "Cascadura",
    "05": "Taquara",
    "06": "Nilopolis",
    "09": "Seropedica",
    "10": "Barra da Tijuca",
    "11": "Campo Grande",
    "13": "Mangueira",
    "14": "Marica",
    "15": "Ilha do Governador",
    "16": "Freguesia",
    "17": "Recreio dos Bandeirantes"
}

def conectar_banco():
    try:
        conn = psycopg2.connect(
            dbname="BOLETOS",
            user="postgres",
            password="postgres",
            host="192.168.1.163"
        )
        return conn
    except psycopg2.Error as e:
        logger.error(f"Erro ao conectar ao PostgreSQL: {str(e)}")
        return None

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

def inserir_log_boletos(mat, cot, destinatario, conn):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO log_boletos (mat, cot, destinatario, data_tentativa)
            VALUES (%s, %s, %s, now())
            """,
            (mat, cot, destinatario)
        )
        conn.commit()
        logger.info(f"Log inserido para mat: {mat}, cot: {cot}, destinatario: {destinatario}")
    except psycopg2.Error as e:
        logger.error(f"Erro ao inserir log na tabela log_boletos: {str(e)}")
    finally:
        cursor.close()

def testar_log_todas_unidades():
    conn = conectar_banco()
    if not conn:
        logger.error("Falha na conexão com o banco. Teste abortado.")
        return

    try:
        for prefixo, unidade_nome in UNIDADES.items():
            logger.info(f"Processando unidade: {unidade_nome} (prefixo: {prefixo})")
            cursor = conn.cursor()
            # Selecionar contatos da unidade com a cota mais recente
            cursor.execute(
                """
                SELECT mat, nome, cot, email
                FROM boletos_geral
                WHERE LEFT(mat, 2) = %s
                AND cot = (SELECT MAX(cot) FROM boletos_geral WHERE LEFT(mat, 2) = %s)
                AND token IS NOT NULL
                AND AGE(now(), geracao) < INTERVAL '28 days'
                ORDER BY mat
                """,
                (prefixo, prefixo)
            )
            rows = cursor.fetchall()

            if not rows:
                logger.info(f"Nenhum contato encontrado para {unidade_nome} com a cota mais recente.")
                continue

            for row in rows:
                mat, nome, cot, email = row
                logger.info(f"Processando contato: mat={mat}, nome={nome}, cot={cot}, email={email}, unidade={unidade_nome}")
                # Extrair e validar e-mails
                emails_validos = extrair_emails([email])
                for email_valido in emails_validos:
                    # Registrar tentativa na tabela log_boletos
                    inserir_log_boletos(mat, cot, email_valido, conn)
                    logger.info(f"Tentativa de envio simulada para {email_valido} (unidade: {unidade_nome})")

    except psycopg2.Error as e:
        logger.error(f"Erro ao consultar contatos: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    testar_log_todas_unidades()