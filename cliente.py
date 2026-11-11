from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder


class ModbusClientHelper:

    def __init__(self, host="127.0.0.1", port=502):
        self.host = host
        self.port = port
        self.client = None

    def connect(self) -> bool:
        self.client = ModbusTcpClient(self.host, port=self.port)
        return self.client.connect()

    def disconnect(self):
        if self.client:
            self.client.close()
            self.client = None

    def is_connected(self) -> bool:
        return self.client is not None and self.client.socket is not None

    def read_coils(self, address: int, count: int = 1):
        if not self.is_connected():
            return None
        res = self.client.read_coils(address, count)
        if res.isError():
            return None
        return res.bits[:count]

    def write_coil(self, address: int, value: bool) -> bool:
        if not self.is_connected():
            return False
        res = self.client.write_coil(address, value)
        return not res.isError()

    def read_holding_registers(self, address: int, count: int = 1):
        if not self.is_connected():
            return None
        res = self.client.read_holding_registers(address, count)
        if res.isError():
            return None
        return res.registers

    def write_holding_register(self, address: int, value: int) -> bool:
        if not self.is_connected():
            return False
        res = self.client.write_register(address, int(value))
        return not res.isError()

    def read_float(
        self,
        address: int,
        word_order=Endian.Big,
        byte_order=Endian.Big,
        div: float = 1.0,
    ):
        registers = self.read_holding_registers(address, 2)
        if not registers:
            return None
        decoder = BinaryPayloadDecoder.fromRegisters(
            registers, byteorder=byte_order, wordorder=word_order
        )
        val_raw = decoder.decode_32bit_float()
        return val_raw / div

    def write_float(
        self,
        address: int,
        value: float,
        word_order=Endian.Big,
        byte_order=Endian.Big,
        div: float = 1.0,
    ) -> bool:
        val_scaled = float(value) * div
        builder = BinaryPayloadBuilder(
            byteorder=byte_order, wordorder=word_order
        )
        builder.add_32bit_float(val_scaled)
        payload = builder.to_registers()
        if not self.is_connected():
            return False
        res = self.client.write_registers(address, payload)
        return not res.isError()

    def read_bits_from_register(self, address: int):
        regs = self.read_holding_registers(address, 1)
        if not regs:
            return None
        val = regs[0]
        return [(val >> i) & 1 for i in range(16)]

    def write_bit_in_register(
        self, address: int, bit_index: int, bit_value: int
    ) -> bool:
        if not (0 <= bit_index <= 15) or bit_value not in (0, 1):
            return False
        regs = self.read_holding_registers(address, 1)
        if not regs:
            return False
        current_val = regs[0]
        if bit_value == 1:
            new_val = current_val | (1 << bit_index)
        else:
            new_val = current_val & ~(1 << bit_index)
        return self.write_holding_register(address, new_val)