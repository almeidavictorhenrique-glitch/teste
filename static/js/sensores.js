async function verificarSensores() {
    try {
        const resposta = await fetch("/sensores");
        const dados = await resposta.json();

        const infoClima = document.getElementById("infoClima");

        let textoClima = "";

        if (dados.temperatura !== null && dados.umidade !== null) {
            textoClima = `🌡️ ${dados.temperatura}°C | 💧 ${dados.umidade}%`;
        } else {
            textoClima = "⏳ Lendo sensor...";
        }

        if (dados.voucher_clima !== null) {
            textoClima += `<br>🎟️ ${dados.voucher_clima.mensagem}`;

            if (dados.voucher_clima.codigo) {
                textoClima += `<br>Código: ${dados.voucher_clima.codigo}`;
            }
        }

        infoClima.innerHTML = textoClima;

    } catch (erro) {
        console.log("Erro ao buscar sensores:", erro);
    }
}

setInterval(verificarSensores, 2000);
verificarSensores();