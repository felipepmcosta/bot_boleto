import datetime
import sys
import jwt
from dataBase import Database

# Chave secreta para assinatura dos tokens JWT
SECRET_KEY = "teste"

# Função para gerar o token JWT
def gerar_token(cot, mat):
    # Concatenando avaliação e matrícula numa variável única
    payload_value = f"{mat}{cot}"
    
    # Dados a serem incluídos no payload do token
    payload = {
        "payload_value": payload_value,
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

        for contato in contatos:
            matricula = contato['mat']
            cot = contato['cot']
            
            # Verificar se o token existe e se a estrutura é válida
            token_valido = False
            if contato['token'] is not None:
                try:
                    decoded_token = jwt.decode(contato['token'], SECRET_KEY, algorithms=["HS256"])
                    if decoded_token.get("payload_value") == f"{matricula}{cot}":
                        token_valido = True
                except (jwt.ExpiredSignatureError, jwt.DecodeError):
                    print(f"Token inválido ou expirado para {matricula} - {cot}. Gerando um novo token.")
            
            if not token_valido:
                token = gerar_token(cot, matricula)
                contato['token'] = token
                dataBase.inserir_token(matricula, cot, token)
                print(f"Token gerado e salvo para {matricula} - {cot}: {token}")
            else:
                print(f"Token já existente e válido para {matricula} - {cot}: {contato['token']}")

        # Commit de todas as alterações
        dataBase.commit()
        print("Geração de tokens concluída.")
    finally:
        dataBase.close()