from flask import Flask, render_template, request, jsonify
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from sensores import iniciar_sensores, estado_sensores, registrar_criador_voucher
from flask_cors import CORS
from datetime import datetime, timedelta
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import random
import string
from datetime import datetime
import qrcode
from qr import gerar_qr_code
import os
import asyncio
import uuid
import json


app = Flask(__name__)
app.secret_key = "interacxflexmedia"
CORS(app)

client = ElevenLabs(
    api_key="sk_8532089d1bd381764bcb2ce143b57fc53f8d90fbc5784e0d"
)

iniciar_sensores()
print("sensores chamados no apppy")

metricas = {
    "interacoes": 0,
    "idiomas": {
        "pt": 0,
        "en": 0
    },
    "animais": {},
    "vouchers": 0,
    "perguntas": []
}

def gerar_insights():
    insights = []

    if metricas["interacoes"] == 0:
        return ["Ainda não há dados suficientes para gerar insights."]

    if metricas["idiomas"]["pt"] > metricas["idiomas"]["en"]:
        insights.append("A maioria dos usuários está utilizando o totem em português.")
    elif metricas["idiomas"]["en"] > metricas["idiomas"]["pt"]:
        insights.append("Usuários estrangeiros estão utilizando bastante o totem em inglês.")

    if metricas["animais"]:
        animal_top = max(metricas["animais"], key=metricas["animais"].get)
        insights.append(f"O animal mais pesquisado até agora é: {animal_top}.")

    if metricas["vouchers"] > 0:
        insights.append(f"Foram gerados {metricas['vouchers']} vouchers até o momento.")

    if metricas["interacoes"] >= 5:
        insights.append("O totem apresenta bom nível de engajamento dos visitantes.")

    return insights

ADMIN_USER = "admin"

ADMIN_PASSWORD_HASH = generate_password_hash("1234")

@app.route("/admin/login", methods=["GET", "POST"])
def login_admin():
    erro = None

    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        if usuario == ADMIN_USER and check_password_hash(ADMIN_PASSWORD_HASH, senha):
            session["admin_logado"] = True
            return redirect(url_for("dashboard"))
        else:
            erro = "Usuário ou senha inválidos"

    return render_template("login_admin.html", erro=erro)


@app.route("/admin/logout")
def logout_admin():
    session.pop("admin_logado", None)
    return redirect(url_for("login_admin"))

def gerar_audio_elevenlabs(texto):
    audio = client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
        text=texto
    )

    nome_arquivo = f"resposta_{uuid.uuid4().hex}.mp3"
    caminho = f"static/audio/{nome_arquivo}"

    os.makedirs("static/audio", exist_ok=True)

    with open(caminho, "wb") as f:
        for chunk in audio:
            f.write(chunk)

    return caminho

# 🧠 "Banco de dados" temporário
vouchers = {}

# 📁 Definir caminho seguro do arquivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_DADOS = os.path.join(BASE_DIR, "dados.txt")
ARQUIVO_INTERACOES = os.path.join(BASE_DIR, "interacoes.json")

def carregar_interacoes():
    if os.path.exists(ARQUIVO_INTERACOES):
        with open(ARQUIVO_INTERACOES, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def salvar_interacoes():
    with open(ARQUIVO_INTERACOES, "w", encoding="utf-8") as f:
        json.dump(interacoes, f, ensure_ascii=False, indent=4)

interacoes = carregar_interacoes()

# 🔢 Gerar código único
def gerar_codigo():
    return "ZOO" + ''.join(random.choices(string.digits, k=5))

# 🎟️ Criar voucher
def criar_voucher(tipo="geral", desconto=10):
    codigo = gerar_codigo()

    vouchers[codigo] = {
        "tipo": tipo,
        "desconto": desconto,
        "usado": False,
        "criado_em": datetime.now(),
        "expira_em": datetime.now() + timedelta(minutes=30)
    }

    return codigo


# Disponibiliza o criador de voucher real para a thread de sensores (voucher de clima).
registrar_criador_voucher(criar_voucher)


# 🌐 HOME
@app.route("/")
def home():
    return render_template("index.html")

# 🎤 PROCESSAMENTO DE VOZ
@app.route("/processar", methods=["POST"])
def processar():
    data = request.json
    pergunta = data.get("texto", "").lower()

    if "leão" in pergunta:
        resposta = "O leão fica na área da savana."
    elif "banheiro" in pergunta:
        resposta = "Os banheiros estão próximos à entrada."
    else:
        resposta = "Desculpe, não entendi sua pergunta."

    caminho_audio = gerar_audio_elevenlabs(resposta)

    interacoes.append({
        "pergunta": pergunta,
        "idioma": "pt",
        "resposta": resposta,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })

    salvar_interacoes()

    return jsonify({
        "resposta": resposta,
        "audio": "/" + caminho_audio
    })

@app.route("/pacotes")
def pacotes():
    idioma = request.args.get("idioma", "pt")
    return render_template("pacotes.html", idioma=idioma)

# 🌐 PERGUNTAS (AGORA SALVANDO NO dados.txt)
@app.route("/pergunta", methods=["POST"])
def pergunta():
    data = request.json or {}
    texto = data.get("texto", "").lower()
    idioma = data.get("idioma", "pt")

    print(f"[LOG] Pergunta recebida: {texto}")

    resposta = "Pergunta registrada!"
    codigo = None
    desconto = None

    if "leao" in texto or "leão" in texto or "lion" in texto:
        resposta = "The lion is known as the king of the jungle!" if idioma == "en" else "O leão é conhecido como o rei da selva!"
        desconto = 15
        codigo = criar_voucher("pelucia_leao", desconto)

    elif "elefante" in texto or "elephant" in texto:
        resposta = "Elephants are the largest land animals!" if idioma == "en" else "Elefantes são os maiores animais terrestres!"
        desconto = 15
        codigo = criar_voucher("pelucia_elefante", desconto)

    elif "girafa" in texto or "giraffe" in texto:
        resposta = "The giraffe is the tallest animal in the world!" if idioma == "en" else "A girafa é o animal mais alto do mundo!"
        desconto = 15
        codigo = criar_voucher("pelucia_girafa", desconto)

    elif "tigre" in texto or "tiger" in texto:
        resposta = "Each tiger has unique stripes!" if idioma == "en" else "Cada tigre possui listras únicas!"
        desconto = 15
        codigo = criar_voucher("pelucia_tigre", desconto)

    elif "arara" in texto or "macaw" in texto:
        resposta = "Macaws can imitate sounds and are very intelligent birds!" if idioma == "en" else "Araras conseguem imitar sons e são aves muito inteligentes!"
        desconto = 15
        codigo = criar_voucher("pelucia_arara", desconto)

    elif "zebra" in texto:
        resposta = "No two zebras have the same stripe pattern!" if idioma == "en" else "Nenhuma zebra possui listras iguais!"
        desconto = 15
        codigo = criar_voucher("pelucia_zebra", desconto)

    else:
        resposta = "Sorry, I didn't understand your question." if idioma == "en" else "Desculpe, não entendi sua pergunta."

    print(f"[LOG] Resposta gerada: {resposta}")

    caminho_audio = gerar_audio_elevenlabs(resposta)

    interacoes.append({
        "pergunta": texto,
        "idioma": idioma,
        "resposta": resposta,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    })

    salvar_interacoes()

    metricas["interacoes"] += 1
    metricas["perguntas"].append(texto)

    if idioma in metricas["idiomas"]:
        metricas["idiomas"][idioma] += 1

    animal = None
    texto_lower = texto.lower()

    if "tigre" in texto_lower or "tiger" in texto_lower:
        animal = "Tigre"
    elif "arara" in texto_lower or "macaw" in texto_lower:
        animal = "Arara"
    elif "zebra" in texto_lower:
        animal = "Zebra"
    elif "leão" in texto_lower or "leao" in texto_lower or "lion" in texto_lower:
        animal = "Leão"
    elif "elefante" in texto_lower or "elephant" in texto_lower:
        animal = "Elefante"
    elif "girafa" in texto_lower or "giraffe" in texto_lower:
        animal = "Girafa"

    if animal:
        metricas["animais"][animal] = metricas["animais"].get(animal, 0) + 1

    if codigo:
        metricas["vouchers"] += 1

    # 💾 SALVAR NO ARQUIVO
    with open(ARQUIVO_DADOS, "a", encoding="utf-8") as f:
        f.write(
            f"{datetime.now()} | idioma: {idioma} | pergunta: {texto} | voucher: {codigo}\n"
        )

    return jsonify({
    "resposta": resposta,
    "audio": "/" + caminho_audio,
    "voucher": codigo,
    "desconto": desconto,
    "tipo": vouchers[codigo]["tipo"] if codigo else None,
    "mensagem": (
        f"Use this code at the store for {desconto}% OFF!"
        if idioma == "en"
        else f"Use este código na loja para {desconto}% de desconto!"
    ) if codigo else None,
    "expira_em": vouchers[codigo]["expira_em"].strftime("%H:%M") if codigo else None
})

@app.route("/dados")
def dados():
    total = len(interacoes)

    idiomas = {
        "pt": sum(1 for i in interacoes if i["idioma"] == "pt"),
        "en": sum(1 for i in interacoes if i["idioma"] == "en")
    }

    perguntas = [i["pergunta"] for i in interacoes]

    total_vouchers = len(vouchers)

    vouchers_por_tipo = {}

    for v in vouchers.values():
        tipo = v["tipo"]
        vouchers_por_tipo[tipo] = vouchers_por_tipo.get(tipo, 0) + 1

    return jsonify({
    "total_interacoes": total,
    "perguntas": perguntas,
    "idiomas": idiomas,
    "ultimas_interacoes": interacoes[-10:],
    "total_vouchers": total_vouchers,
    "vouchers_por_tipo": vouchers_por_tipo
})


@app.route("/dashboard")
def dashboard():
    if not session.get("admin_logado"):
        return redirect(url_for("login_admin"))

    return render_template("dashboard.html")

@app.route("/dados-dashboard")
def dados_dashboard():
    return jsonify({
        "metricas": metricas,
        "insights": gerar_insights()
    })


@app.route("/stats")
def stats():
    total = len(vouchers)
    usados = sum(1 for v in vouchers.values() if v.get("usado"))
    disponiveis = total - usados

    return jsonify({
        "total": total,
        "usados": usados,
        "disponiveis": disponiveis,
        "total_vouchers": total
    })

@app.route("/gerar-qr")
def gerar_qr():

    link_final = "http://127.0.0.1:5000/experiencia-final"

    caminho = gerar_qr_code(link_final)

    return jsonify({
        "qr": "/" + caminho,
        "mensagem": "QR Code gerado com sucesso!"
    })

@app.route("/experiencia-final")
def experiencia_final():
    return render_template("experiencia_final.html")

@app.route("/sensores")
def sensores():
    print("ROTA /sensores ACESSADA", flush=True)
    print(estado_sensores, flush=True)
    return jsonify(estado_sensores)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )
