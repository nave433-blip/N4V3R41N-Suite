import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QLabel, QComboBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from offline_cloudpass import OfflineCloudPass

class ExploitWorker(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, cloudpass, exploit_name):
        super().__init__()
        self.cloudpass = cloudpass
        self.exploit_name = exploit_name

    def run(self):
        self.log_signal.emit(f"[*] Executing {self.exploit_name}...")
        response = self.cloudpass.execute_bypass(self.exploit_name)
        if response:
            self.log_signal.emit(f"[+] Status: {response.status_code}")
        else:
            self.log_signal.emit("[-] Bypass failed.")

class N4V3R41N_GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("N4V3R41N Suite v9.6 - Armageddon Control")
        self.setGeometry(100, 100, 800, 600)
        self.cloudpass = OfflineCloudPass()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.label = QLabel("Select Exploit Vector:")
        layout.addWidget(self.label)

        self.exploit_combo = QComboBox()
        self.exploit_combo.addItems(self.cloudpass.exploits.keys())
        layout.addWidget(self.exploit_combo)

        self.btn_run = QPushButton("Deploy Armageddon")
        self.btn_run.setStyleSheet("background-color: #ff4444; color: white; font-weight: bold;")
        self.btn_run.clicked.connect(self.run_exploit)
        layout.addWidget(self.btn_run)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

    def run_exploit(self):
        exploit = self.exploit_combo.currentText()
        self.worker = ExploitWorker(self.cloudpass, exploit)
        self.worker.log_signal.connect(self.log_area.append)
        self.worker.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = N4V3R41N_GUI()
    window.show()
    sys.exit(app.exec())
