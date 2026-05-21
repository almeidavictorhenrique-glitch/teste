import time
import threading
import platform
import random

IS_WINDOWS = platform.system() == "Windows"

if not IS_WINDOWS:
    import board
    import adafruit_dht

estado_sensores = {
    "presenca": True,
    "distancia": 55,
    "temperatura": None,
    "umidade": None,
    "voucher_clima": None
}

# Referência ao criador de voucher real (injetada pelo app.py via registrar_criador_voucher).
# Evita import circular: o app.py já importa deste módulo.
criar_voucher_fn = None

def registrar_criador_voucher(fn):
    global criar_voucher_fn
    criar_voucher_fn = fn

def definir_voucher_clima(temperatura, umidade):
    if temperatura is None or umidade is None:
        return None

    if temperatura >= 28:
        return {
            "tipo": "calor",
            "desconto": 15,
            "mensagem": "Está calor! Ganhe 15% de desconto em bebidas geladas."
        }

    if temperatura < 18:
        return {
            "tipo": "frio",
            "desconto": 15,
            "mensagem": "Está frio! Ganhe 15% de desconto em bebidas quentes."
        }

    # Faixa agradável (18 a 27°C): voucher de lanche.
    return {
        "tipo": "lanche",
        "desconto": 15,
        "mensagem": "Que tempo bom! Ganhe 15% de desconto em lanches."
    }

def loop_sensores():
    print("THREAD DOS SENSORES INICIOU", flush=True)

    # Cria o sensor UMA vez só, fora do loop.
    # Recriar a cada volta gera conflito no GPIO e faz a leitura falhar sempre.
    dht = None
    if not IS_WINDOWS:
        dht = adafruit_dht.DHT11(board.D17, use_pulseio=False)

    # Controla pra gerar código novo só quando o clima MUDA,
    # senão criaríamos um voucher a cada 3 segundos.
    tipo_clima_atual = None

    while True:
        if IS_WINDOWS:
            temperatura = random.randint(24, 34)
            umidade = random.randint(50, 85)

            estado_sensores["temperatura"] = temperatura
            estado_sensores["umidade"] = umidade

        else:
            try:
                temperatura = dht.temperature
                umidade = dht.humidity

                print("DHT LIDO:", temperatura, umidade, flush=True)

                if temperatura is not None and umidade is not None:
                    estado_sensores["temperatura"] = temperatura
                    estado_sensores["umidade"] = umidade

            except RuntimeError as e:
                # Falha de leitura é normal no DHT11, só tenta de novo na próxima volta.
                print("Falha DHT (tentando de novo):", e, flush=True)

            except Exception as e:
                print("Erro DHT:", e, flush=True)

        voucher = definir_voucher_clima(
            estado_sensores["temperatura"],
            estado_sensores["umidade"]
        )

        if voucher is None:
            estado_sensores["voucher_clima"] = None
            tipo_clima_atual = None

        elif voucher["tipo"] != tipo_clima_atual:
            # O clima mudou: gera um código real (se o app.py já registrou o criador).
            if criar_voucher_fn is not None:
                voucher["codigo"] = criar_voucher_fn(voucher["tipo"], voucher["desconto"])
                tipo_clima_atual = voucher["tipo"]
                estado_sensores["voucher_clima"] = voucher
            else:
                # Criador ainda não registrado: mostra a mensagem sem código por enquanto
                # e tenta gerar o código na próxima volta (tipo_clima_atual segue None).
                estado_sensores["voucher_clima"] = voucher

        # Se o clima é o mesmo, mantém o voucher anterior (com o mesmo código).

        print("ESTADO FINAL:", estado_sensores, flush=True)

        time.sleep(3)

def iniciar_sensores():
    print("FUNÇÃO iniciar_sensores() CHAMADA", flush=True)

    thread = threading.Thread(
        target=loop_sensores,
        daemon=True
    )

    thread.start()
