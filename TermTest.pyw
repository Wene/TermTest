#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtSerialPort import *
from PyQt5.QtWidgets import *


class Form(QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        layout = QGridLayout(self)

        self.port_selector = QComboBox()
        self.port_selector.addItem("Select Port...")
        self.speed_selector = QComboBox()
        layout.addWidget(self.port_selector, 0, 0)
        layout.addWidget(self.speed_selector, 0, 1)

        port_list = QSerialPortInfo.availablePorts()
        for port in port_list:
            assert isinstance(port, QSerialPortInfo)
            port_name = port.portName() + " (" + port.manufacturer() + " / " + port.description() + ")"
            self.port_selector.addItem(port_name, port)

        self.port_selector.currentIndexChanged.connect(self.port_selected)

    def port_selected(self):
        self.speed_selector.clear()
        port = self.port_selector.currentData()
        if isinstance(port, QSerialPortInfo):
            speed_list = port.standardBaudRates()
            for speed in speed_list:
                self.speed_selector.addItem(str(speed), speed)


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
