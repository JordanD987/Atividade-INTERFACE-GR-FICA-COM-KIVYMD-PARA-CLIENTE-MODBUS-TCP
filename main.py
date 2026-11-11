from cliente import ModbusClientHelper
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField

KV = """
MDBoxLayout:
    orientation: 'vertical'
    padding: 16
    spacing: 12

    MDLabel:
        text: "Supervisório Modbus TCP - KivyMD"
        font_style: "H5"
        halign: "center"
        size_hint_y: None
        height: self.texture_size[1]

    MDBoxLayout:
        spacing: 8
        size_hint_y: None
        height: "56dp"
        MDTextField:
            id: txt_ip
            text: "127.0.0.1"
            hint_text: "IP Servidor"
        MDTextField:
            id: txt_port
            text: "502"
            hint_text: "Porta"
        MDButton:
            id: btn_connect
            on_release: app.toggle_connection()
            MDButtonText:
                id: btn_connect_text
                text: "Conectar"

    MDBoxLayout:
        spacing: 8
        size_hint_y: None
        height: "40dp"
        MDLabel:
            text: "Tipo de Dado:"
            size_hint_x: None
            width: "100dp"
        MDButton:
            on_release: app.set_data_type("Holding Register")
            MDButtonText:
                text: "Holding Reg"
        MDButton:
            on_release: app.set_data_type("Float")
            MDButtonText:
                text: "Float32"
        MDButton:
            on_release: app.set_data_type("Coil")
            MDButtonText:
                text: "Coil"
        MDButton:
            on_release: app.set_data_type("Bit")
            MDButtonText:
                text: "Bit no Reg"

    MDLabel:
        id: lbl_selected_type
        text: "Tipo Selecionado: Holding Register"
        theme_text_color: "Secondary"
        size_hint_y: None
        height: "20dp"

    MDBoxLayout:
        spacing: 8
        size_hint_y: None
        height: "56dp"
        MDTextField:
            id: txt_address
            text: "830"
            hint_text: "Endereço Modbus"
        MDTextField:
            id: txt_bit_index
            text: "6"
            hint_text: "Índice do Bit (0-15)"
        MDTextField:
            id: txt_write_val
            text: "0"
            hint_text: "Valor p/ Escrita"

    MDBoxLayout:
        spacing: 8
        size_hint_y: None
        height: "48dp"
        MDCheckbox:
            id: chk_recurrent
            size_hint: None, None
            size: "48dp", "48dp"
            on_active: app.on_recurrent_check(self, self.active)
        MDLabel:
            text: "Leitura Recorrente (1s)"
            valign: "center"
        MDButton:
            on_release: app.read_data()
            MDButtonText:
                text: "Ler"
        MDButton:
            on_release: app.write_data()
            MDButtonText:
                text: "Escrever"

    MDLabel:
        text: "Resultado:"
        bold: True
        size_hint_y: None
        height: "24dp"

    MDLabel:
        id: lbl_result
        text: "Aguardando ação..."
        halign: "left"
        valign: "top"
"""


class ModbusApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.modbus = ModbusClientHelper()
        self.current_type = "Holding Register"
        self.clock_event = None

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)

    def toggle_connection(self):
        if not self.modbus.is_connected():
            ip = self.root.ids.txt_ip.text
            port = int(self.root.ids.txt_port.text)
            self.modbus.host = ip
            self.modbus.port = port
            if self.modbus.connect():
                self.root.ids.btn_connect_text.text = "Desconectar"
                self.root.ids.lbl_result.text = (
                    f"Conectado com sucesso em {ip}:{port}"
                )
            else:
                self.root.ids.lbl_result.text = "Falha ao conectar no servidor!"
        else:
            self.modbus.disconnect()
            self.root.ids.btn_connect_text.text = "Conectar"
            self.root.ids.lbl_result.text = "Desconectado."
            if self.clock_event:
                self.clock_event.cancel()
                self.clock_event = None

    def set_data_type(self, dtype):
        self.current_type = dtype
        self.root.ids.lbl_selected_type.text = f"Tipo Selecionado: {dtype}"

    def on_recurrent_check(self, checkbox, value):
        if value:
            self.clock_event = Clock.schedule_interval(self.read_data, 1.0)
        else:
            if self.clock_event:
                self.clock_event.cancel()
                self.clock_event = None

    def read_data(self, dt=None):
        if not self.modbus.is_connected():
            self.root.ids.lbl_result.text = "Erro: Cliente Modbus desconectado."
            return

        try:
            addr = int(self.root.ids.txt_address.text)
            if self.current_type == "Holding Register":
                val = self.modbus.read_holding_registers(addr, 1)
                self.root.ids.lbl_result.text = f"Holding Reg [{addr}]: {val}"
            elif self.current_type == "Float":
                val = self.modbus.read_float(addr)
                self.root.ids.lbl_result.text = f"Float32 [{addr}]: {val}"
            elif self.current_type == "Coil":
                val = self.modbus.read_coils(addr, 1)
                self.root.ids.lbl_result.text = f"Coil [{addr}]: {val}"
            elif self.current_type == "Bit":
                bits = self.modbus.read_bits_from_register(addr)
                self.root.ids.lbl_result.text = f"Bits Reg [{addr}]: {bits}"
        except Exception as e:
            self.root.ids.lbl_result.text = f"Erro de Leitura: {str(e)}"

    def write_data(self):
        if not self.modbus.is_connected():
            self.root.ids.lbl_result.text = "Erro: Cliente Modbus desconectado."
            return

        try:
            addr = int(self.root.ids.txt_address.text)
            raw_val = self.root.ids.txt_write_val.text

            if self.current_type == "Holding Register":
                success = self.modbus.write_holding_register(
                    addr, int(raw_val)
                )
            elif self.current_type == "Float":
                success = self.modbus.write_float(addr, float(raw_val))
            elif self.current_type == "Coil":
                val_bool = raw_val.lower() in ("1", "true", "t")
                success = self.modbus.write_coil(addr, val_bool)
            elif self.current_type == "Bit":
                bit_idx = int(self.root.ids.txt_bit_index.text)
                bit_val = int(raw_val)
                success = self.modbus.write_bit_in_register(
                    addr, bit_idx, bit_val
                )

            status = "Sucesso" if success else "Falha"
            self.root.ids.lbl_result.text = (
                f"Escrita ({self.current_type}) em [{addr}]: {status}"
            )
        except Exception as e:
            self.root.ids.lbl_result.text = f"Erro de Escrita: {str(e)}"


if __name__ == "__main__":
    ModbusApp().run()