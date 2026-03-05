from pathlib import Path

from playsound3 import playsound
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)


class AlarmUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self) -> None:
        self.main_lyt = QVBoxLayout()
        # TODO: this is a QWindow, use toolbar , mainwidget
        self.lbl_workout = QLabel("Workout")
        self.lbl_breakfast = QLabel("Breakfast")
        self.alarm_lyt = QVBoxLayout()
        self.alarm_lyt.addWidget(self.lbl_workout)
        self.alarm_lyt.addWidget(self.lbl_breakfast)

        self.main_lyt.addLayout(self.alarm_lyt)

        self.central_wgt = QWidget()
        self.central_wgt.setLayout(self.main_lyt)
        self.setCentralWidget(self.central_wgt)

    def main(self):
        playsound(Path("~/test.mp3"))


if __name__ == "__main__":
    app = QApplication([])
    window = AlarmUI()
    # skyline_ico = QPixmap(r"N:\pipeline\Tools\icons\skyline.ico")
    # window.setWindowIcon(skyline_ico)
    window.setWindowTitle("Reminder")
    window.setWindowFlags(window.windowFlags() | Qt.WindowMinimizeButtonHint)
    window.setWindowFlags(window.windowFlags() | Qt.WindowMaximizeButtonHint)
    window.showMaximized()
    window.resize(1200, 800)
    app.exec()
