#!/usr/bin/env python3

# TermTest is a test environment for a serial terminal.
# Copyright (C) 2015  Werner Meier <wene83@gmx.ch>
#
# This license (GPL v3) is applied because of the license terms of a
# library (PyQt) I use in this project.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5.QtCore import *
from PyQt5.QtSerialPort import *
from PyQt5.QtWidgets import *


class Form(QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        layout = QVBoxLayout(self)

        # restore saved settings
        self.settings = QSettings("Wene", "TermTest")
        self.move(self.settings.value("Position", QPoint(10, 10), type=QPoint))
        self.resize(self.settings.value("Size", QSize(100, 100), type=QSize))

        # define timer and buffer
        self.buffer = ""
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.empty_buffer)

        # define port selection layout and widgets
        lay_select = QHBoxLayout()
        layout.addLayout(lay_select)
        self.port_selector = QComboBox()
        self.port_selector.currentIndexChanged.connect(self.port_selected)
        self.speed_selector = QComboBox()
        # enable resizing after widget gets first shown
        self.speed_selector.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.speed_selector.currentIndexChanged.connect(self.speed_selected)
        self.btn_connect = QPushButton("&Verbinden")
        self.btn_connect.setEnabled(False)
        self.btn_connect.clicked.connect(self.connect_to_serial)
        lay_select.addWidget(self.port_selector)
        lay_select.addWidget(self.speed_selector)
        lay_select.addWidget(self.btn_connect)
        lay_select.addStretch()
        self.fill_port_selector()

        # define input widgets
        self.inbox = QTextEdit()
        self.inbox.setReadOnly(True)
        layout.addWidget(self.inbox)

        # define output widgets
        lay_output = QHBoxLayout()
        layout.addLayout(lay_output)
        self.template_selector = QComboBox()
        self.fill_template_selector()
        lay_output.addWidget(self.template_selector)
        self.input = QLineEdit()
        self.input.setToolTip("<p>Zeichen als Dezimalzahlen durch Leerzeichen getrennt eingeben</p>")
        lay_output.addWidget(self.input)
        self.btn_send = QPushButton("&Senden")
        lay_output.addWidget(self.btn_send)
        self.input.returnPressed.connect(self.btn_send.click)
        self.btn_send.clicked.connect(self.send_data)

        # define serial port
        self.serial_port = QSerialPort()

    # search for available serial ports and fill the QComboBox
    def fill_port_selector(self):
        self.port_selector.clear()
        self.port_selector.addItem("Port auswählen...")
        port_list = QSerialPortInfo.availablePorts()
        for port in port_list:
            assert isinstance(port, QSerialPortInfo)
            port_name = port.portName() + " (" + port.manufacturer() + " / " + port.description() + ")"
            self.port_selector.addItem(port_name, port)

        # append dummy port for local simulation
        port_name = "/dev/pts/2 (Dummy)"
        port = "Dummy"  # String to identify the dummy port
        self.port_selector.addItem(port_name, port)

        # restore last time selected port
        port_setting = self.settings.value("Port", type=int)
        speed_setting = self.settings.value("Speed", type=int)
        if isinstance(port_setting, int):
            self.port_selector.setCurrentIndex(port_setting)
        if isinstance(speed_setting, int):
            self.speed_selector.setCurrentIndex(speed_setting)

    # fill the QComboBox with commands from http://www.vt100.net/docs/vt510-rm/contents
    def fill_template_selector(self):
        self.template_selector.addItem("Vorlage wählen...")
        self.template_selector.addItem("Links", "27 91 49 68")
        self.template_selector.addItem("Rechts", "27 91 49 67")
        self.template_selector.addItem("Aufwärts", "27 91 49 65")
        self.template_selector.addItem("Abwärts", "27 91 49 66")
        self.template_selector.addItem("Display löschen", "27 91 50 74")
        self.template_selector.addItem("Cursor zum Anfang", "27 91 49 59 49 72")
        self.template_selector.addItem("Cursor Position abfragen", "27 91 54 110")
        self.template_selector.addItem("Host LED Modus", "27 91 63 49 49 48 104")
        self.template_selector.addItem("Caps LED ein", "27 91 50 113")
        self.template_selector.addItem("Caps LED aus", "27 91 50 50 113")
        # When a command is selected, the input field content is replaced with the command.
        self.template_selector.currentIndexChanged.connect(self.template_selected)

    # this slot is called by selecting another serial port -> list the available speed settings
    def port_selected(self):
        self.speed_selector.clear()
        port = self.port_selector.currentData()
        if isinstance(port, QSerialPortInfo):  # the first and the dummy aren't QSerialPortInfo. They're just text.
            self.speed_selector.addItem("Geschwindigkeit...")
            speed_list = port.standardBaudRates()
            for speed in speed_list:
                self.speed_selector.addItem(str(speed), speed)
        elif isinstance(port, str):  # If it's the dummy, set speed also to dummy
            if port == "Dummy":
                self.speed_selector.addItem("Geschwindigkeit...")
                self.speed_selector.addItem("Dummy", 0)

    # This slot is called by selecting a speed. If valid the btn_connect gets enabled.
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
            self.inbox.append("verbinde...")
            self.serial_port.setPort(port)
            self.serial_port.setBaudRate(speed)
            connected = self.serial_port.open(QIODevice.ReadWrite)
            self.inbox.append("Verbindung: " + str(connected))
            if connected:
                self.serial_port.readyRead.connect(self.read_serial)
                self.port_selector.setEnabled(False)
                self.speed_selector.setEnabled(False)
                self.btn_connect.setEnabled(False)
            else:
                self.inbox.append("Fehler: " + self.serial_port.errorString())

        # local test dummy for use with socat
        # [socat -d -d pty,raw,echo=0,user=<username> pty,raw,echo=0,user=<username>]
        elif isinstance(port, str) and port == "Dummy":
            self.inbox.append("verbinde...")
            self.serial_port.setPortName("/dev/pts/2")  # replace port number when needed
            connected = self.serial_port.open(QIODevice.ReadWrite)
            self.inbox.append("Verbindung: " + str(connected))
            if connected:
                self.serial_port.readyRead.connect(self.read_serial)
                self.port_selector.setEnabled(False)
                self.speed_selector.setEnabled(False)
                self.btn_connect.setEnabled(False)
            else:
                self.inbox.append("Fehler: " + self.serial_port.errorString())
            # connection from the other side is made by [screen /dev/pts/3]

    # This slot is called whenever new data is available for read.
    def read_serial(self):
        data = self.serial_port.read(self.serial_port.bytesAvailable())
        assert isinstance(data, bytes)
        for character in data:
            self.buffer += str(int(character))
            self.buffer += " "
        self.timer.start()  # Start or restart the timer til the buffer is displayed. Therefore it's
                            # possible to show one transmission in one line.

    # After timer times out, the buffer is shown and reset.
    def empty_buffer(self):
        self.inbox.append(self.buffer)
        self.buffer = ""

    # This slot is called by pressing the btn_send. Sends Data to the terminal.
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

    def template_selected(self):
        command = self.template_selector.currentData()
        if isinstance(command, str):
            self.input.clear()
            self.input.setText(command)

    # save settings
    def closeEvent(self, QCloseEvent):
        self.settings.setValue("Position", self.pos())
        self.settings.setValue("Size", self.size())
        self.serial_port.close()
        self.settings.setValue("Port", self.port_selector.currentIndex())
        self.settings.setValue("Speed", self.speed_selector.currentIndex())


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
