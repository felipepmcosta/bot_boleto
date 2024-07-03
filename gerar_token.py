import datetime
import sys
import jwt  
from dataBase import Database

# Chave secreta para assinatura dos tokens JWT
SECRET_KEY = "teste"

# Função para gerar o token JWT
def gerar_token(cot, mat):
    # Dados a serem incluídos no payload do token
    payload = {
        "cot": cot,
        "mat": mat,
    }
    # Gerar o token JWT assinado
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

if __name__ == "__main__":
    dataBase = Database()
    try:
        # Obtendo os contatos com base nos dois primeiros dígitos de 'mat' e 'cot' da função pega_contatos_teste()
        contatos = dataBase.pega_contatos_db()

        # Se não houver contatos disponíveis, exiba uma mensagem e saia
        if not contatos:
            print("Não foram encontrados contatos para gerar tokens. Todos já foram gerados.")
            sys.exit(1)

        hoje = datetime.date.today()
        dia_do_mes = hoje.day

        for contato in contatos:
            matricula = contato['mat']
            cot = contato['cot']

            # Verificar se o campo 'token' está vazio
            if not contato['token'] and contato['boleto'] is not None:
                # Gerar um novo token apenas se o campo estiver vazio
                token = gerar_token(cot, matricula)
                # Atualizar o campo 'token' no dicionário de contato
                contato['token'] = token
                # Salvar o token no banco de dados
                dataBase.inserir_token(matricula, token)
                print(f"Token gerado e salvo para {matricula}: {token}")
            else:
                # Se o campo 'token' já estiver preenchido, ignore
                print(f"Token já existente para {matricula}: {contato['token']}")

        # Commit de todas as alterações
        dataBase.commit()
        print("Geração de tokens concluída.")
    finally:
        dataBase.close()
