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

    def inserir_token(self, mat, cot, token):
        try:
            self.cursor.execute("UPDATE boletos_geral SET token = %s WHERE mat = %s AND cot = %s AND token IS NULL AND boleto IS NOT NULL", (token, mat, cot))
        except psycopg2.Error as e:
            logger.error("Erro ao inserir token no PostgreSQL: %s", e)

    def commit(self):
        self.conn.commit()

    def pega_contatos_db(self):
        contatos = []
        try:
            self.cursor.execute("SELECT id, mat, nome, cot, boleto, digitavel, token, envio, geracao, created_at, updated_at, email, cpfa, cpf, cpf2, pix FROM boletos_geral")
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
