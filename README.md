# Bot Boleto

Envia por e-mail o link do boleto de cada responsável e valida o link quando ele é aberto. Duas partes: scripts Python que gravam um token por boleto no PostgreSQL e disparam os e-mails, e uma API Node que consulta o boleto e valida o token.

## Requisitos

- Python 3 com `psycopg2`, `requests`, `email-validator` e `PyJWT` (importados pelos scripts; não há `requirements.txt`)
- Node.js e npm para a API em `ValidaBoleto/Backend` (versão exata não verificada)
- PostgreSQL com o banco `BOLETOS` e a tabela `boletos_geral`

## Instalação

```bash
pip install psycopg2-binary requests email-validator PyJWT
cd ValidaBoleto/Backend
npm install
```

(não verificado)

## Configuração

A API lê `ValidaBoleto/Backend/.env`, modelo em `.env.example`.

| Variável | Para que |
|---|---|
| `DB_USER`, `DB_PASS` | usuário e senha do PostgreSQL |
| `DB_NAME`, `DB_HOST`, `DB_PORT` | banco, servidor e porta |

Os scripts Python têm host, banco, usuário e senha do PostgreSQL escritos no código (`db.py`, `dataBase.py`), fora do `.env`.

## Uso

API, na porta 3353:

```bash
cd ValidaBoleto/Backend
npx nodemon src/server.js
```

Gerar tokens e enviar os e-mails (os dois argumentos filtram por prefixo de matrícula e de avaliação; sem eles envia para todos os contatos pendentes):

```bash
cd ValidaBoleto
python token_boletos.py
python enviarBoletos.py <mat_prefix> <cot_prefix>
```

Nenhum dos comandos foi verificado.

## Testes

Não há testes automatizados. `testar_log_br.py` é um script manual que consulta o banco para conferir o registro de envios. (não verificado)

## Estrutura

```
ValidaBoleto/             scripts Python de envio
  token_boletos.py        gera o token JWT de cada boleto
  enviarBoletos.py        envia os e-mails e registra o envio
  boletosAPI.py           versão anterior do envio, via API de e-mail
  db.py, dataBase.py      acesso ao PostgreSQL
  msg.html                modelo do e-mail
ValidaBoleto/Backend/     API Node (Express e Sequelize)
  src/                    servidor e rotas
  controllers/, models/   consulta e validação do boleto
  database/, config/      conexão com o banco
  images/                 imagens do cabeçalho e rodapé do boleto
testar_log_br.py          script de conferência do registro de envios
```
