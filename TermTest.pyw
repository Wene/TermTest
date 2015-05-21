#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtSerialPort import *
from PyQt5.QtWidgets import *


class Form(QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        layout = QVBoxLayout(self)

        # define timer and buffer
        self.buffer = ""
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.empty_buffer)

        # define port selsction layout and widgets
        lay_select = QHBoxLayout()
        layout.addLayout(lay_select)
        self.port_selector = QComboBox()
        self.fill_port_selector()
        self.port_selector.currentIndexChanged.connect(self.port_selected)
        self.speed_selector = QComboBox()
        # enable resizing after widget gets first shown
        self.speed_selector.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.speed_selector.currentIndexChanged.connect(self.speed_selected)
        self.btn_connect = QPushButton("&Connect")
        self.btn_connect.setEnabled(False)
        self.btn_connect.clicked.connect(self.connect_to_serial)
        lay_select.addWidget(self.port_selector)
        lay_select.addWidget(self.speed_selector)
        lay_select.addWidget(self.btn_connect)
        lay_select.addStretch()

        # define input widgets
        self.inbox = QTextEdit()
        self.inbox.setReadOnly(True)
        layout.addWidget(self.inbox)

        # define output widgets
        lay_output = QHBoxLayout()
        layout.addLayout(lay_output)
        self.input = QLineEdit()
        lay_output.addWidget(self.input)
        self.btn_send = QPushButton("&Send")
        lay_output.addWidget(self.btn_send)
        self.input.returnPressed.connect(self.btn_send.click)
        self.btn_send.clicked.connect(self.send_data)

        # define serial port
        self.serial_port = QSerialPort()

        # restore saved settings
        self.settings = QSettings("Wene", "TermTest")
        self.move(self.settings.value("Position", QPoint(10, 10), type=QPoint))
        self.resize(self.settings.value("Size", QSize(100, 100), type=QSize))

    # search for available serial ports and fill the QComboBox
    def fill_port_selector(self):
        self.port_selector.clear()
        self.port_selector.addItem("Select Port...")
        port_list = QSerialPortInfo.availablePorts()
        for port in port_list:
            assert isinstance(port, QSerialPortInfo)
            port_name = port.portName() + " (" + port.manufacturer() + " / " + port.description() + ")"
            self.port_selector.addItem(port_name, port)

    # this slot is called by selecting another serial port -> list the available speed settings
    def port_selected(self):
        self.speed_selector.clear()
        port = self.port_selector.currentData()
        if isinstance(port, QSerialPortInfo):  # the first item isn't a QSerialPortInfo. It's just text.
            self.speed_selector.addItem("Select Speed...")
            speed_list = port.standardBaudRates()
            for speed in speed_list:
                self.speed_selector.addItem(str(speed), speed)

    def speed_selected(self):
        speed = self.speed_selector.currentData()
        if isinstance(speed, int):
            self.btn_connect.setEnabled(True)
        else:
            self.btn_connect.setEnabled(False)

    # establish serial connection with chosen settings
    def connect_to_serial(self):
        port = self.port_selector.currentData()
        speed = self.speed_selector.currentData()
        if isinstance(port, QSerialPortInfo) and isinstance(speed, int):
            self.inbox.append("connecting...")
            self.serial_port.setPort(port)
            self.serial_port.setBaudRate(speed)
            connected = self.serial_port.open(QIODevice.ReadWrite)
            self.inbox.append("Connection: " + str(connected))
            if connected:
                self.serial_port.readyRead.connect(self.read_serial)
                self.port_selector.setEnabled(False)
                self.speed_selector.setEnabled(False)
                self.btn_connect.setEnabled(False)
            else:
                self.inbox.append("Error: " + self.serial_port.errorString())

    def read_serial(self):
        data = self.serial_port.read(self.serial_port.bytesAvailable())
        assert isinstance(data, bytes)
        for character in data:
            self.buffer += str(int(character))
            self.buffer += " "
        self.timer.start()

    def empty_buffer(self):
        self.inbox.append(self.buffer)
        self.buffer = ""

    def send_data(self):
        segments = self.input.text().split()
        characters = bytearray()
        for character in segments:
            if character.isdigit():
                segment = int(character)
                if segment >= 0 and segment < 256:
                    characters.append(segment)
        if len(characters) > 0 and self.serial_port.isOpen():
            self.serial_port.write(characters)


# save settings
    def closeEvent(self, QCloseEvent):
        self.settings.setValue("Position", self.pos())
        self.settings.setValue("Size", self.size())

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    translator = QTranslator()
    lib_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    translator.load("qt_de.qm", lib_path)
    translator.load("qtbase_de.qm", lib_path)
    app.installTranslator(translator)

    window = Form()
    window.show()

    sys.exit(app.exec_())
