import math
import random
import threading
import time
from pyModbusTCP.server import DataBank, ModbusServer
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder

# Instância do banco de dados do servidor
data_bank = DataBank()


def encode_float(value: float) -> list:
    builder = BinaryPayloadBuilder(
        byteorder=Endian.BIG, wordorder=Endian.BIG
    )
    builder.add_32bit_float(value)
    return builder.to_registers()


def decode_float(registers: list) -> float:
    decoder = BinaryPayloadDecoder.fromRegisters(
        registers, byteorder=Endian.BIG, wordorder=Endian.BIG
    )
    return decoder.decode_32bit_float()


def simular_clp():
    """Thread background para atualizar 10 medições simuladas."""
    # Inicializa Setpoint (FP 1302-1303) = 50.0 e Habilita (1328 bit 6) = 1
    data_bank.set_holding_registers(1302, encode_float(50.0))
    data_bank.set_holding_registers(1328, [1 << 6])

    t = 0
    while True:
        # Lê Setpoint e Bit de Habilitação do cliente
        sp_regs = data_bank.get_holding_registers(1302, 2)
        sp_vazao = decode_float(sp_regs) if sp_regs else 50.0

        reg_cmd = data_bank.get_holding_registers(1328, 1)[0]
        motor_habilitado = bool((reg_cmd >> 6) & 1)

        # 1-4. Temperaturas R, S, T e Carcaça (FP 700..707, Div=10)
        base_temp = 25.0 + (5.0 if motor_habilitado else 0.0)
        data_bank.set_holding_registers(
            700, encode_float((base_temp + math.sin(t) * 0.5) * 10)
        )
        data_bank.set_holding_registers(
            702, encode_float((base_temp + 0.2 + math.cos(t) * 0.4) * 10)
        )
        data_bank.set_holding_registers(
            704, encode_float((base_temp - 0.3 + math.sin(t) * 0.3) * 10)
        )
        data_bank.set_holding_registers(
            706, encode_float((base_temp + 2.0 + math.sin(t) * 0.2) * 10)
        )

        # 5. Pressão PIT01 (FP 710-711, Div=1)
        pressao = (
            (sp_vazao * 0.08 + random.uniform(-0.1, 0.1))
            if motor_habilitado
            else 0.0
        )
        data_bank.set_holding_registers(710, encode_float(pressao))

        # 6. Vazão FIT01 (FP 712-713, Div=1)
        vazao = (
            (sp_vazao + random.uniform(-0.5, 0.5)) if motor_habilitado else 0.0
        )
        data_bank.set_holding_registers(712, encode_float(vazao))

        # 7. Frequência (4X 830, Div=100, ex: 60Hz -> 6000)
        freq = int(
            (sp_vazao * 1.2 * 100)
            if motor_habilitado
            else 0
        )
        data_bank.set_holding_registers(830, [max(0, min(6000, freq))])

        # 8. Corrente R (4X 840, Div=10, ex: 12.3A -> 123)
        corrente = int((12.3 * 10) if motor_habilitado else 0)
        data_bank.set_holding_registers(840, [corrente])

        # 9. Tensão R-S (4X 847, Div=10, ex: 220V -> 2200)
        tensao = int((220.0 + random.uniform(-2, 2)) * 10)
        data_bank.set_holding_registers(847, [tensao])

        # 10. Fator de Potência (4X 868, Div=1000, ex: 0.95 -> 950)
        fp = int((0.95 * 1000) if motor_habilitado else 0)
        data_bank.set_holding_registers(868, [fp])

        t += 0.5
        time.sleep(1)


if __name__ == "__main__":
    server = ModbusServer("127.0.0.1", 502, no_block=True, data_bank=data_bank)
    print("Iniciando Servidor Modbus TCP em 127.0.0.1:502...")
    server.start()

    thread_simulacao = threading.Thread(target=simular_clp, daemon=True)
    thread_simulacao.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Encerrando Servidor.")
        server.stop()