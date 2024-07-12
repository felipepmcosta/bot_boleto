import psycopg2
import logging

# Configurando o sistema de logging para o módulo db.py
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="BOLETOS",
            user="postgres",
            password="postgres",
            host="192.168.1.163"
        )
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def inserirToken(self, mat, token):
        try:
            self.cursor.execute("UPDATE boletos_geral SET token = %s WHERE mat = %s AND token IS NULL AND boleto IS NOT NULL", (token, mat))
        except psycopg2.Error as e:
            logger.error("Erro ao inserir token no PostgreSQL: %s", e)

    def commit(self):
        self.conn.commit()

    def atualizar_envio(self, mat):
        try:
            self.cursor.execute("UPDATE boletos_geral SET envio = now() WHERE mat = %s", (mat,))
        except psycopg2.Error as e:
            logger.error("Erro ao atualizar coluna 'envio' no PostgreSQL: %s", e)

    def pega_contatos_db(self, mat_prefix=None, cot_prefix=None):
        contatos = []
        try:
            if mat_prefix is not None and cot_prefix is not None:
                self.cursor.execute("SELECT id, mat, nome, cot, boleto, digitavel, token, envio, geracao, created_at, updated_at, email, cpfa, cpf, cpf2, pix FROM boletos_geral WHERE LEFT(mat, 2) = %s AND cot = %s AND envio is NULL LIMIT 10", (mat_prefix, cot_prefix))
            else:
                self.cursor.execute("SELECT id, mat, nome, cot, boleto, digitavel, token, envio, geracao, created_at, updated_at, email, cpfa, cpf, cpf2, pix FROM boletos_geral WHERE envio is NULL LIMIT 10")
            rows = self.cursor.fetchall()
            for row in rows:
                contatos.append({
                    'id': row[0],
                    'mat': row[1],
                    'nome': row[2],
                    'cot': row[3],
                    'boleto': row[4],
                    'digitavel': row[5],
                    'token': row[6],
                    'envio': row[7],
                    'geracao': row[8],
                    'created_at': row[9],
                    'updated_at': row[10],
                    'email': row[11],
                    'cpfa': row[12],
                    'cpf': row[13],
                    'cpf2': row[14],
                    'pix': row[15]
                })
        except psycopg2.Error as e:
            logger.error("Erro ao conectar ao PostgreSQL: %s", e)

        return contatos

    @staticmethod
    def extrairEmails(camposEmail):
        emails = []
        for campo in camposEmail:
            if campo:
                emails.extend(campo.split(','))

        return [email.strip() for email in emails if email.strip()]
