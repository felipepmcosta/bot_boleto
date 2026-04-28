import os, logging, sys, itertools, requests
from string import Template
from email_validator import validate_email, EmailNotValidError
from db import pega_contatos_db, atualizar_envio, extrair_emails, inserir_log_boletos

args = sys.argv[1:]

if len(args) < 2:
    print("Os argumentos 'mat_prefix' e 'cot_prefix' não foram fornecidos. Enviando boletos para todos os contatos disponíveis...")
    mat_prefix = None
    cot_prefix = None
else:
    mat_prefix = args[0]
    cot_prefix = args[1]

# Verifica se há contatos sem carregar tudo na RAM
_contatos_gen = pega_contatos_db(mat_prefix, cot_prefix)
_primeiro = next(_contatos_gen, None)
if _primeiro is None:
    print("Não foram encontrados contatos para enviar boletos. Todos já foram enviados.")
    sys.exit(1)
contatos = itertools.chain([_primeiro], _contatos_gen)

EMAIL_SENDER = 'boleto@smrede.com.br'
envio_pausado = False

logging.basicConfig(filename='email_logs.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

link = "https://boletos.santamonicarede.com.br/"

# Session única reutilizada em todos os envios (HTTP keep-alive + connection pooling)
_http_session = requests.Session()
_http_session.headers.update({'Content-Type': 'application/json'})


def ler_template(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, filename)
    with open(file_path, 'r', encoding='utf-8') as arquivotemplate:
        return Template(arquivotemplate.read())

def pega_unidade(matricula):
    unidades = {
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
    numero = matricula[:2]
    return unidades.get(numero, "Sem Unidade selecionada")

def obter_mes_ano(cot, geracao):
    meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março",
        4: "Abril", 5: "Maio", 6: "Junho",
        7: "Julho", 8: "Agosto", 9: "Setembro",
        10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    mes_boleto = int(cot)
    mes_geracao = geracao.month
    ano = geracao.year
    if mes_boleto < mes_geracao:
        ano += 1
    return f"{meses.get(mes_boleto, 'Mês Desconhecido')}/{ano}"

def enviarEmail(destinatario, assunto, mensagem, mat, cot):
    envio_destinatarios = extrair_emails([destinatario])
    enviado_com_sucesso = False

    for destinatario_individual in envio_destinatarios:
        try:
            inserir_log_boletos(mat, cot, destinatario_individual)

            unidade = pega_unidade(mat)
            dados_json = {
                "para": destinatario_individual,
                "de": EMAIL_SENDER,
                "assunto": assunto,
                "html": mensagem,
                "categorias": ["Boleto", unidade, cot]
            }

            api_url = 'https://sendmail.smrede.tec.br/sendEmail'
            enviado = sendMessage(dados_json, api_url)

            if enviado:
                logging.info(f'E-mail enviado para {destinatario_individual} usando API.')
                enviado_com_sucesso = True
            else:
                logging.error(f'Falha ao enviar e-mail para {destinatario_individual} usando API.')

        except EmailNotValidError as e:
            logging.error(f"O e-mail '{destinatario_individual}' não está em um formato válido: {str(e)}")
            continue
        except requests.exceptions.RequestException as e:
            logging.error(f'Erro ao enviar e-mail para {destinatario_individual}: {str(e)}')
            continue
        except Exception as e:
            logging.error(f'Erro inesperado ao processar e-mail {destinatario_individual}: {str(e)}')
            continue

    return enviado_com_sucesso

def sendMessage(dados_json, api_url):
    try:
        response = _http_session.post(api_url, json=dados_json, timeout=(5, 30))

        if response.status_code == 200:
            unidade = dados_json["categorias"][1] if len(dados_json["categorias"]) > 1 else "Unidade não especificada"
            logging.info(f'E-mail enviado para {dados_json["para"]}. Unidade: {unidade}')
            return True
        else:
            error_message = response.text if response.text else "Sem mensagem de erro detalhada"
            logging.error(f'Falha ao enviar e-mail usando API para {dados_json["para"]}. Status code: {response.status_code}. Resposta: {error_message}')
            return False

    except requests.exceptions.RequestException as e:
        logging.error(f'Erro ao enviar e-mail usando API: {str(e)}')
        return False

try:
    mensagem_template = ler_template('msg.html')
    emails_falha_vistos = set()

    for contato in contatos:
        if envio_pausado:
            logging.info('Envio de e-mails pausado.')
            break
        try:
            nome = contato['nome']
            mat = contato['mat']
            cot = contato['cot']
            unidade = pega_unidade(mat)
            email = contato['email']
            token = contato['token']
            linkToken = f"{link}{token}"
            geracao = contato['geracao']
            mensagem = mensagem_template.substitute(
                PERSON_NAME=nome.title(),
                LINK=linkToken,
                MES_ANO=obter_mes_ano(contato['cot'], geracao),
                UNIDADE=unidade
            )
            assunto = f"Seu BOLETO SMREDE - Unidade {unidade} chegou!!!"
            enviado = enviarEmail(email, assunto, mensagem, mat, cot)

            if enviado:
                atualizar_envio(mat)
            else:
                if email not in emails_falha_vistos:
                    emails_falha_vistos.add(email)
                    logging.warning(f'Falha no envio para {email} (mat={mat}, unidade={unidade})')

        except Exception as ex:
            logging.error(f'Erro ao processar contato {contato["mat"]}: {str(ex)}')
            continue

except Exception as ex:
    logging.error('Erro geral ao iniciar o envio de e-mails: %s', ex)
