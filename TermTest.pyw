#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtSerialPort import *
from PyQt5.QtWidgets import *


class Form(QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        layout = QGridLayout(self)
        debug = QTextEdit()
        layout.addWidget(debug, 0, 0)
        debug.setReadOnly(True)

        port_list = QSerialPortInfo.availablePorts()
        for port in port_list:
            assert isinstance(port, QSerialPortInfo)
            debug.append(port.portName())
            debug.append(port.manufacturer())
            debug.append(port.serialNumber())
            debug.append(port.description())
            debug.append(port.systemLocation())
            debug.append("Speeds:")
            speeds = port.standardBaudRates()
            for speed in speeds:
                debug.append(str(speed))


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
