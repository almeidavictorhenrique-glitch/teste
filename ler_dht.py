import json
import time
import board
import adafruit_dht

resultado = {
    "temperatura": None,
    "umidade": None
}

dht = adafruit_dht.DHT11(board.D17, use_pulseio=False)

while True:
    try:
        temperatura = dht.temperature
        umidade = dht.humidity

        resultado["temperatura"] = temperatura
        resultado["umidade"] = umidade

        break

    except RuntimeError:
        time.sleep(2)

print(json.dumps(resultado))
