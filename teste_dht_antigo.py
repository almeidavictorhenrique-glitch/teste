import Adafruit_DHT
import time

SENSOR = Adafruit_DHT.DHT11
PIN = 17

while True:
    umidade, temperatura = Adafruit_DHT.read_retry(SENSOR, PIN)

    if umidade is not None and temperatura is not None:
        print(f"Temperatura: {temperatura:.1f}°C")
        print(f"Umidade: {umidade:.1f}%")
    else:
        print("Falha ao ler o DHT")

    time.sleep(2)
