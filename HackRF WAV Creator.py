import os
import sys
from subprocess import getoutput
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class Worker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, input_file, output_file):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file

    def run(self):
        output = getoutput(f'ffmpeg -i "{self.input_file}" -ar 48000 -ac 1 -acodec pcm_u8 "{self.output_file}.wav"')
        success = 'size' in output.lower()
        self.finished.emit(success, output)

class AudioConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.dark_theme = True
        self.initUI()

    def initUI(self):
        self.setWindowTitle("HackRF WAV Creator")
        self.setStyleSheet(self.get_style())

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        self.label = QLabel("Select an .mp3 file:")
        self.label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.label)

        self.entry = QLineEdit(self)
        layout.addWidget(self.entry)

        button_layout = QHBoxLayout()

        self.browse_button = QPushButton("Browse")
        self.browse_button.setObjectName("browse_button")
        self.browse_button.clicked.connect(self.select_file)
        button_layout.addWidget(self.browse_button)

        self.convert_button = QPushButton("Convert to .wav")
        self.convert_button.setObjectName("convert_button")
        self.convert_button.clicked.connect(self.convert_file)
        button_layout.addWidget(self.convert_button)

        self.theme_button = QPushButton("Toggle Theme")
        self.theme_button.setObjectName("theme_button")
        self.theme_button.clicked.connect(self.toggle_theme)
        button_layout.addWidget(self.theme_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_style(self):
        if self.dark_theme:
            return """
                QWidget {
                    background-color: #3C3C3C; 
                    font-family: Arial;
                    color: #FFFFFF;
                }
                QLineEdit {
                    background-color: #505050; 
                    color: #FFFFFF; 
                    padding: 8px; 
                    border-radius: 4px;
                }
                QPushButton {
                    border-radius: 4px; 
                    padding: 10px;
                }
                QPushButton#browse_button {
                    background-color: #4CAF50; 
                    color: #FFFFFF;
                }
                QPushButton#convert_button {
                    background-color: #2196F3; 
                    color: #FFFFFF;
                }
                QPushButton#theme_button {
                    background-color: #FFC107; 
                    color: #000000;
                }
                QMessageBox {
                    background-color: #3C3C3C;
                    color: #FFFFFF;
                }
                QMessageBox QPushButton {
                    background-color: #4CAF50;
                    color: #FFFFFF;
                }
            """
        else:
            return """
                QWidget {
                    background-color: #FFFFFF; 
                    font-family: Arial;
                    color: #000000;
                }
                QLineEdit {
                    background-color: #F0F0F0; 
                    color: #000000; 
                    padding: 8px; 
                    border-radius: 4px;
                }
                QPushButton {
                    border-radius: 4px; 
                    padding: 10px;
                }
                QPushButton#browse_button {
                    background-color: #8BC34A; 
                    color: #000000;
                }
                QPushButton#convert_button {
                    background-color: #2196F3; 
                    color: #FFFFFF;
                }
                QPushButton#theme_button {
                    background-color: #FFEB3B; 
                    color: #000000;
                }
                QMessageBox {
                    background-color: #FFFFFF;
                    color: #000000;
                }
                QMessageBox QPushButton {
                    background-color: #2196F3;
                    color: #FFFFFF;
                }
            """

    def toggle_theme(self):
        self.dark_theme = not self.dark_theme
        self.setStyleSheet(self.get_style())

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select an .mp3 file", "", "Audio Files (*.mp3)")
        if file_path:
            self.entry.setText(file_path)

    def convert_file(self):
        input_file = self.entry.text().strip()
        if not input_file:
            QMessageBox.warning(self, "Input Error", "Please enter the name of the file.")
            return
        output_name = os.path.splitext(input_file)[0]

        self.worker = Worker(input_file, output_name)
        self.worker.finished.connect(self.on_conversion_finished)
        self.worker.start()

    def on_conversion_finished(self, success, output):
        if success:
            QMessageBox.information(self, "Success", f"The transformation of the file {self.entry.text()} into {os.path.splitext(self.entry.text())[0]}.wav was completed successfully.")
        else:
            QMessageBox.critical(self, "Error", "Unknown error. Please ensure that you have entered the correct name.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    converter = AudioConverter()
    converter.show()
    sys.exit(app.exec_())
