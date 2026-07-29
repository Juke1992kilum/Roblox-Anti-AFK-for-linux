from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QSpinBox, QVBoxLayout
)


class MacroUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sober Macro Controller")

        self.interval_label = QLabel("Interval (seconds):")

        self.interval_input = QSpinBox()
        self.interval_input.setRange(1, 3600)
        self.interval_input.setValue(5)

        self.coord_button = QPushButton("Set Click Position")
        self.coord_label = QLabel("Position: (not set)")

        self.toggle_button = QPushButton("Start")
        self.toggle_button.setCheckable(True)

        layout = QVBoxLayout()
        layout.addWidget(self.interval_label)
        layout.addWidget(self.interval_input)
        layout.addWidget(self.coord_button)
        layout.addWidget(self.coord_label)
        layout.addWidget(self.toggle_button)

        self.setLayout(layout)