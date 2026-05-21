from gtts import gTTS
import os

os.makedirs("static/audios", exist_ok=True)

texto_pt = """
Bem-vindo ao zoológico!
Você pode explorar o mapa,
conhecer os animais
e descobrir curiosidades incríveis.
"""

texto_en = """
Welcome to the zoo!
You can explore the map,
learn about the animals
and discover amazing facts.
"""

audio_pt = gTTS(
    text=texto_pt,
    lang="pt"
)

audio_pt.save(
    "static/audios/bemvindo_pt.mp3"
)

audio_en = gTTS(
    text=texto_en,
    lang="en"
)

audio_en.save(
    "static/audios/bemvindo_en.mp3"
)

print("Áudios criados com sucesso!")
