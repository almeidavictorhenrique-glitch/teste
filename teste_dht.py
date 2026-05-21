import time
import board
import adafruit_dht

dht = adafruit_dht.DHT11(board.D17)

while True:
    try:
        temperatura = dht.temperature
        umidade = dht.humidity

        print("Temperatura:", temperatura)
        print("Umidade:", umidade)

    except RuntimeError as e:
        print("Falha:", e)

    time.sleep(2)
