import pyautogui


class Controller(object):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    ENTER = "enter"

    def __init__(self):
        self.delay = 0.05
        self.pre_input_key = None
        self.post_input_key = None

    def write(self, text):
        pyautogui.write(text, interval=self.delay)

    def press(self, key):
        pyautogui.press(key)

    def input_cell(self, value):
        if self.pre_input_key is not None:
            self.press(self.pre_input_key)
        self.write(value)
        if self.post_input_key is not None:
            self.press(self.post_input_key)

    def input_cells(self, values, move_dir):
        for value in values:
            self.input_cell(value)
            self.press(move_dir)

    def set_delay(self, delay):
        self.delay = delay

    def set_pre_input(self, key):
        self.pre_input_key = key

    def set_post_input(self, key):
        self.post_input_key = key
