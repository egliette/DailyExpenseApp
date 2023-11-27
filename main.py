import sys

from PyQt5.QtWidgets import QApplication

from ui.login_ui import LoginUI


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = LoginUI()
    w.show()
    app.exec()