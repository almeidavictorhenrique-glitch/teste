import qrcode

def gerar_qr_code(texto, caminho="static/qrcode.png"):

    img = qrcode.make(texto)

    img.save(caminho)

    return caminho