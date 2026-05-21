function iniciarVoz() {

    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

    recognition.lang = (idioma === "en") ? "en-US" : "pt-BR";
    recognition.continuous = false;
    recognition.interimResults = false;

    let terminou = false;

    recognition.onstart = () => {
        console.log("🎤 Gravando...");
    };

    recognition.onresult = (event) => {
        terminou = true;

        const texto = event.results[0][0].transcript.toLowerCase();

        console.log("✅ Você disse:", texto);

        recognition.stop();

        irPara("pergunta");

        setTimeout(() => {
            const input = document.getElementById("texto");

            if (input) {
                input.value = texto;
            }

            enviar();

        }, 200);
    };

    recognition.onerror = (event) => {
        console.error("❌ Erro:", event.error);
        recognition.stop();
    };

    recognition.onend = () => {
        console.log("⛔ Parou de ouvir");

        if (!terminou) {
            console.log("⚠️ Nenhuma fala detectada");
        }
    };

    setTimeout(() => {
        recognition.stop();
    }, 4000);

    recognition.start();
}


/* Clica no animal e envia automaticamente */
let animalSelecionado = "";

function selecionarAnimal(animal){
    animalSelecionado = animal;

    document.getElementById("texto").value = animal;

    mostrarNoMapa(animal);

    enviar();
}


// 🌍 Detecta tela pela URL
const params = new URLSearchParams(window.location.search);

const telaURL = params.get("tela");

if(telaURL){

    setTimeout(() => {

        irPara(telaURL);

    }, 100);
}