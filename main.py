import subprocess
import time

from pynput import mouse
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from ui import MacroUI


class MacroController:
    def __init__(self, ui):
        self.ui = ui

        self.user_workspace = 0
        self.sober_workspace = 1

        self.interval = 5

        self.click_x = None
        self.click_y = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.click_sober)

        self.capturing = False

    # -------------------------
    # RUN COMMAND
    # -------------------------
    def run(self, cmd):
        subprocess.run(cmd, shell=True)

    # -------------------------
    # GET MOUSE POSITION
    # -------------------------
    def get_mouse_pos(self):
        out = subprocess.check_output(
            "xdotool getmouselocation --shell",
            shell=True
        ).decode()

        data = {}
        for line in out.splitlines():
            if "=" in line:
                k, v = line.split("=")
                data[k] = int(v)

        return data["X"], data["Y"]

    # -------------------------
    # FAST CLICK (STABLE)
    # -------------------------
    def instant_click(self, x, y):
        # move + click immediately (min latency)
        self.run(f"xdotool mousemove {x} {y} click 1")
        self.run(f"xdotool mousemove {x} {y} click 1")

    # -------------------------
    # MAIN MACRO LOOP
    # -------------------------
    def click_sober(self):
        try:
            orig_x, orig_y = self.get_mouse_pos()

            # 1. switch to target workspace
            self.run(f"xdotool set_desktop {self.sober_workspace}")
            time.sleep(0.05)

            # 2. determine target position
            if self.click_x is not None:
                x, y = self.click_x, self.click_y
            else:
                out = subprocess.check_output(
                    "xdotool getdisplaygeometry",
                    shell=True
                ).decode().strip()

                w, h = map(int, out.split())
                x, y = w // 2, h // 2

            # 3. CLICK PHASE (critical)
            self.instant_click(x, y)

            # 4. IMPORTANT: allow X11 to fully process click state
            # prevents stuck drag / text highlight on return workspace
            time.sleep(0.03)

            # extra safety: force release state cleanup
            self.run("xdotool mouseup 1")

            # 5. now safe to return workspace
            self.run(f"xdotool set_desktop {self.user_workspace}")

            # 6. restore cursor last
            self.run(f"xdotool mousemove {orig_x} {orig_y}")

        except Exception as e:
            print("Macro error:", e)

    # -------------------------
    # START / STOP
    # -------------------------
    def start(self):
        self.timer.start(self.interval * 1000)

    def stop(self):
        self.timer.stop()

    # -------------------------
    # CAPTURE CLICK POSITION
    # -------------------------
    def start_capture(self):
        if self.capturing:
            return

        self.capturing = True
        self.ui.coord_label.setText("Click anywhere to set position...")

        def on_click(x, y, button, pressed):
            if pressed:
                self.click_x = x
                self.click_y = y

                self.ui.coord_label.setText(
                    f"Position: ({x}, {y})"
                )

                print("Saved coords:", x, y)

                self.capturing = False
                return False

        mouse.Listener(on_click=on_click).start()


# -------------------------
# MAIN APP
# -------------------------
def main():
    app = QApplication([])
    app.setApplicationName("Anti AFK")
    app.setDesktopFileName("Anti AFK.desktop") 

    ui = MacroUI()
    controller = MacroController(ui)

    ui.interval_input.valueChanged.connect(
        lambda v: setattr(controller, "interval", v)
    )

    def toggle():
        if ui.toggle_button.isChecked():
            controller.start()
            ui.toggle_button.setText("Stop")
        else:
            controller.stop()
            ui.toggle_button.setText("Start")

    ui.toggle_button.clicked.connect(toggle)
    ui.coord_button.clicked.connect(controller.start_capture)

    ui.show()
    app.exec()


if __name__ == "__main__":
    main()