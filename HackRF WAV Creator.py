import os
import sys
from subprocess import getoutput
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSignal, QObject, QPropertyAnimation


class WorkerSignals(QObject):
    finished = pyqtSignal(bool, str)


class Worker(QRunnable):
    def __init__(self, input_file, output_file):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.signals = WorkerSignals()

    def run(self):
        output = getoutput(f'ffmpeg -i "{self.input_file}" -ar 48000 -ac 1 -acodec pcm_u8 "{self.output_file}.wav"')
        success = 'size' in output.lower()
        self.signals.finished.emit(success, output)


class AudioConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.dark_theme = True
        self.initUI()
        self.pool = QThreadPool()
        self.success_count = 0
        self.error_count = 0

    def initUI(self):
        self.setWindowTitle("HackRF WAV Creator")
        self.setStyleSheet(self.get_style())
        self.setWindowOpacity(0.9)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        self.label = QLabel("Select .mp3 files:")
        self.label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.label)

        self.entry = QLineEdit(self)
        layout.addWidget(self.entry)

        button_layout = QHBoxLayout()

        self.browse_button = QPushButton("Browse")
        self.browse_button.setObjectName("browse_button")
        self.browse_button.clicked.connect(self.select_files)
        button_layout.addWidget(self.browse_button)

        self.convert_button = QPushButton("Convert to .wav")
        self.convert_button.setObjectName("convert_button")
        self.convert_button.clicked.connect(self.convert_files)
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
                    color: #FFFFFF;
                }
                QPushButton#browse_button {
                    background-color: #4CAF50; 
                }
                QPushButton#convert_button {
                    background-color: #2196F3; 
                }
                QPushButton#theme_button {
                    background-color: #FFC107; 
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
                    color: #000000;
                }
                QPushButton#browse_button {
                    background-color: #8BC34A; 
                }
                QPushButton#convert_button {
                    background-color: #2196F3; 
                }
                QPushButton#theme_button {
                    background-color: #FFEB3B; 
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
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0.90)
        self.animation.setEndValue(0.0)

        self.animation.finished.connect(self.change_theme)
        self.animation.start()

    def change_theme(self):
        self.dark_theme = not self.dark_theme
        self.setStyleSheet(self.get_style())

        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(0.90)
        self.animation.start()

    def select_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select .mp3 files", "", "Audio Files (*.mp3)")
        if file_paths:
            self.entry.setText(", ".join(file_paths))

    def convert_files(self):
        self.success_count = 0
        self.error_count = 0

        file_names = self.entry.text().strip().split(", ")
        if not file_names or all(not fn for fn in file_names):
            QMessageBox.warning(self, "Input Error", "Please enter the names of the files.")
            return

        for input_file in file_names:
            input_file = input_file.strip()
            output_name = os.path.splitext(input_file)[0]
            worker = Worker(input_file, output_name)

            worker.signals.finished.connect(self.on_conversion_finished)

            self.pool.start(worker)

    def on_conversion_finished(self, success, output):
        if success:
            self.success_count += 1
        else:
            self.error_count += 1

        if self.success_count + self.error_count == self.pool.activeThreadCount() + self.success_count + self.error_count:
            if self.error_count == 0:
                QMessageBox.information(self, "Success", f"Successfully processed {self.success_count} files.")
            else:
                QMessageBox.warning(self, "Conversion Results", 
                                    f"Processed {self.success_count} files successfully, "
                                    f"but there were {self.error_count} errors.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    converter = AudioConverter()
    converter.show()
    sys.exit(app.exec_())