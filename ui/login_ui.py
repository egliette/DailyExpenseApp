from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QMainWindow

from ui import resources_rc
from ui.dashboard_ui import DashboardUI


class LoginUI(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("ui/login.ui", self)
        self.setWindowTitle("Login")
        self.setWindowIcon(QtGui.QIcon(":/images/icon"))

        self.nextButton.clicked.connect(self.open_dashboard)
        
    def open_dashboard(self):
        username = self.usernameEdit.text().strip()
        if len(username) == 0:
            username = "User"
        self.close()
        self.window = DashboardUI(username)
        self.window.showMaximized() 
 