# ENE118 - Comunicação Industrial & Supervisório Modbus TCP (KivyMD)

## Integrantes
* **Integrante 1**: Desenvolvimento da classe de comunicação Modbus (`cliente.py`).
* **Integrante 2**: Implementação da interface gráfica (`main.py`) e do servidor de emulação (`servidor.py`).

---

## 📋 Mapa de Dados Emulado (Bancada de Bombeamento)

| Tag / Dado | Tipo | Endereços | Div (D) | Multiplicador | Unidade | Descrição |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `bc.temp_r` | FP (Float32) | 700-701 | 10 | 0.1 | °C | Temperatura da fase R |
| `bc.temp_s` | FP (Float32) | 702-703 | 10 | 0.1 | °C | Temperatura da fase S |
| `bc.temp_t` | FP (Float32) | 704-705 | 10 | 0.1 | °C | Temperatura da fase T |
| `bc.temp_carc` | FP (Float32) | 706-707 | 10 | 0.1 | °C | Temperatura da Carcaça |
| `bc.pit01` | FP (Float32) | 710-711 | 1 | 1 | bar | Pressão da bomba |
| `bc.fit01` | FP (Float32) | 712-713 | 1 | 1 | m³/h | Vazão medida |
| `bc.frequencia` | Inteiro (4X) | 830 | 100 | 0.01 | Hz | Frequência do inversor |
| `bc.corrente_r` | Inteiro (4X) | 840 | 10 | 0.1 | A | Corrente da fase R |
| `bc.tensao_rs` | Inteiro (4X) | 847 | 10 | 0.1 | V | Tensão entre fases R-S |
| `bc.fp_r` | Inteiro (4X) | 868 | 1000 | 0.001 | - | Fator de Potência R |
| `bc.sp_pid` | FP (Float32) | 1302-1303 | 1 | 1 | m³/h | Setpoint de Vazão enviado pelo cliente |
| `bc.habilita` | Bit (4X) | 1328 (Bit 6) | 1 | 1 | - | Comando: Habilita/Desabilita motor (1/0) |

* **Ordem das Palavras**: Big Endian.

---

## 🚀 Passo a Passo Exato para Executar sem Erros

1. Instalar as dependências:
   ```bash
   pip install -r requirements.txt