from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QDoubleSpinBox, QFrame,
                             QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QGridLayout, QSpinBox, QComboBox, QCheckBox,
                             QSizePolicy)
from PyQt5.QtCore import QTimer, Qt, QSettings
from PyQt5.QtGui import QIcon, QClipboard
from controller import Controller
from concurrent.futures import ThreadPoolExecutor
import resources


def text_to_values(text):
    values = text.split()
    values = [v.strip() for v in values]
    values = [v if v != "-" else "0" for v in values]
    return values


def main():
    app = QApplication([])
    window = QWidget()
    layout = QVBoxLayout()
    executor = ThreadPoolExecutor(max_workers=1)

    edit = QLineEdit()

    def update_cb():
        cb = QApplication.clipboard()
        edit.setText(cb.text())

    cb_timer = QTimer()
    cb_timer.timeout.connect(update_cb)

    def use_cb_checked(checked):
        edit.setEnabled(not checked)
        if checked:
            cb_timer.start(500)
        else:
            cb_timer.stop()

    use_cb = QCheckBox()
    use_cb.stateChanged.connect(use_cb_checked)

    paste_delay = QSpinBox()

    input_delay = QDoubleSpinBox()
    input_delay.setSingleStep(0.01)

    pre_post_key = QComboBox()
    pre_post_key.addItem("None", None)
    pre_post_key.addItem("Enter", Controller.ENTER)

    move_dir = QComboBox()
    move_dir.addItem("Left", Controller.LEFT)
    move_dir.addItem("Right", Controller.RIGHT)
    move_dir.addItem("Up", Controller.UP)
    move_dir.addItem("Down", Controller.DOWN)

    def load_settings():
        q_settings = QSettings("MySoft", "TablePaster")
        paste_delay.setValue(int(q_settings.value("paste_delay", 5)))
        input_delay.setValue(float(q_settings.value("input_delay", 0.05)))
        pre_post_key.setCurrentIndex(int(q_settings.value("pre_post_key", 1)))
        move_dir.setCurrentIndex(int(q_settings.value("move_dir", 1)))
        use_cb.setChecked(bool(q_settings.value("use_clipboard", False)))

    def save_settings():
        q_settings = QSettings("MySoft", "TablePaster")
        q_settings.setValue("paste_delay", paste_delay.value())
        q_settings.setValue("input_delay", input_delay.value())
        q_settings.setValue("pre_post_key", pre_post_key.currentIndex())
        q_settings.setValue("move_dir", move_dir.currentIndex())
        q_settings.setValue("use_clipboard", use_cb.isChecked())

    app.aboutToQuit.connect(save_settings)

    load_settings()

    settings = QFrame()
    settings_layout = QGridLayout()
    settings_layout.setContentsMargins(0, 0, 0, 0)
    settings.setLayout(settings_layout)

    settings_layout.addWidget(QLabel("Paste delay (sec.): "), 0, 0)
    settings_layout.addWidget(paste_delay, 0, 1)
    settings_layout.addWidget(QLabel("Input delay (sec.): "), 1, 0)
    settings_layout.addWidget(input_delay, 1, 1)
    settings_layout.addWidget(QLabel("Input start/end: "), 2, 0)
    settings_layout.addWidget(pre_post_key, 2, 1)
    settings_layout.addWidget(QLabel("Move direction: "), 3, 0)
    settings_layout.addWidget(move_dir, 3, 1)
    settings_layout.addWidget(QLabel("Use clipboard: "), 4, 0)
    settings_layout.addWidget(use_cb, 4, 1)

    is_pasting = False

    def paste_items():
        nonlocal is_pasting
        is_pasting = True
        if use_cb.isChecked():
            cb = QApplication.clipboard()
            text = cb.text()
        else:
            text = edit.text()
        values = text_to_values(text)
        ctrl = Controller()
        ctrl.set_pre_input(pre_post_key.currentData())
        ctrl.set_post_input(pre_post_key.currentData())
        ctrl.set_delay(input_delay.value())
        ctrl.input_cells(values, move_dir.currentData())
        is_pasting = False

    def start_pasting_items():
        executor.submit(paste_items)

    paste_timer = QTimer()
    paste_timer.timeout.connect(start_pasting_items)
    paste_timer.setSingleShot(True)

    def start_timer():
        time_delay = paste_delay.value() * 1000
        paste_timer.start(time_delay)

    def stop_timer():
        paste_timer.stop()

    start_button = QPushButton("Start")
    start_button.setStyleSheet("QPushButton {color: green;}")
    start_button.clicked.connect(start_timer)

    stop_button = QPushButton("Cancel")
    stop_button.setStyleSheet("QPushButton {color: red;}")
    stop_button.clicked.connect(stop_timer)

    up_arrow_sym = '\u2191'
    down_arrow_sym = '\u2193'

    settings_button = QPushButton("Settings " + up_arrow_sym)

    def toggle_settings():
        width = window.width()
        settings.setHidden(not settings.isHidden())
        is_hidden = settings.isHidden()
        text_add = down_arrow_sym if is_hidden else up_arrow_sym
        settings_button.setText("Settings " + text_add)
        window.adjustSize()
        window.resize(width, window.height())

    settings_button.clicked.connect(toggle_settings)

    info_label = QLabel()
    info_label.setStyleSheet("QLabel {color: magenta;}")

    def update_label():
        if is_pasting:
            info_label.setText("Pasting...")
        elif paste_timer.isActive():
            time = paste_timer.remainingTime()
            info_label.setText(f"Seconds until paste: {round(time / 1000, 1)}")
        else:
            info_label.setText("Press 'Start' to paste")

    update_timer = QTimer()
    update_timer.timeout.connect(update_label)
    update_timer.start(200)

    buttons = QHBoxLayout()
    buttons.addWidget(settings_button)
    buttons.addWidget(stop_button)
    buttons.addWidget(start_button)

    edit_layout = QHBoxLayout()
    edit_layout.addWidget(QLabel("Values:"))
    edit_layout.addWidget(edit)

    layout.addLayout(edit_layout)
    layout.addLayout(buttons)
    layout.addWidget(settings)
    layout.addWidget(info_label)

    version = "1.0.1"

    size_policy = window.sizePolicy()
    size_policy.setVerticalPolicy(QSizePolicy.Minimum)
    window.setLayout(layout)
    window.setWindowTitle(f"Table Paster v{version}")
    window.resize(480, 200)
    window.setWindowFlags(Qt.WindowStaysOnTopHint)
    window.setWindowIcon(QIcon(":/icons/table.ico"))
    window.show()
    app.exec()


if __name__ == '__main__':
    main()

