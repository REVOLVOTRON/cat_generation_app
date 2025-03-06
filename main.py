import sys
from PyQt6 import QtWidgets
from ui import CatGeneratorApp


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = CatGeneratorApp()
    window.show()
    sys.exit(app.exec())