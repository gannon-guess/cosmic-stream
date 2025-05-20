import tkinter as tk
from tkinter import ttk
import obsws_python as obsws
import json
import os

import obs_cameras as cameras
import obs_lineup as lineup
from obs_timer import CountdownTimer
from obs_clock import Clock

# OBS connection details
host = "localhost"
port = 4455
password = "secret"

PRESET_FOLDER = "presets"
os.makedirs(PRESET_FOLDER, exist_ok=True)


class OBSControlGUI:
    def __init__(self, master):
        self.ws = obsws.ReqClient(host=host, port=port, password=password)

        # Data
        self.schools = lineup.lineup
        self.school_dropdown_options = ["None"] + self.schools + ["All"]

        self.camera_names = cameras.camera_names
        self.cam_dropdown_options = ["Off"] + self.camera_names

        # GUI Root
        self.master = master
        master.title("OBS Controller")
        master.geometry("400x800")
        master.resizable(False, False)

        # Team Selection
        self.team_var = tk.StringVar()
        ttk.Label(master, text="Highlighted Team:").pack(pady=(10, 0))
        self.team_dropdown = ttk.Combobox(
            master,
            textvariable=self.team_var,
            values=self.school_dropdown_options,
            state="readonly",
        )
        self.team_dropdown.pack(fill="x", padx=20)
        self.team_dropdown.current(0)

        # Camera Mode
        self.mode_var = tk.StringVar(value="split")
        ttk.Label(master, text="Camera Mode:").pack(pady=(15, 0))
        frame = ttk.Frame(master)
        frame.pack(pady=5)
        ttk.Radiobutton(
            frame, text="Split (4)", variable=self.mode_var, value="split"
        ).pack(side="left", padx=10)
        ttk.Radiobutton(
            frame, text="Full (1)", variable=self.mode_var, value="full"
        ).pack(side="left", padx=10)

        # Camera Dropdowns
        self.cam_vars = [
            tk.StringVar(value=self.cam_dropdown_options[1]) for _ in range(4)
        ]
        positions = ["Top Left", "Top Right", "Bottom Left", "Bottom Right"]
        self.cam_dropdowns = []

        for i, pos in enumerate(positions):
            ttk.Label(master, text=f"{pos} Camera:").pack(pady=(10 if i == 0 else 5, 0))
            dropdown = ttk.Combobox(
                master,
                textvariable=self.cam_vars[i],
                values=self.cam_dropdown_options,
                state="readonly",
            )
            dropdown.pack(fill="x", padx=20)
            self.cam_dropdowns.append(dropdown)

        # Confirm Button
        ttk.Button(master, text="Confirm", command=self.apply_changes).pack(pady=20)

        # Preset controls
        ttk.Label(master, text="Preset Slot:").pack(pady=(5, 0))
        self.preset_var = tk.StringVar(value="Slot 1")
        self.preset_dropdown = ttk.Combobox(
            master,
            textvariable=self.preset_var,
            values=[f"Slot {i+1}" for i in range(5)],
            state="readonly",
        )
        self.preset_dropdown.pack(fill="x", padx=20)

        btn_frame = ttk.Frame(master)
        btn_frame.pack(pady=(5, 15))

        ttk.Button(btn_frame, text="Save", command=self.save_preset).pack(
            side="left", padx=10
        )
        ttk.Button(btn_frame, text="Load", command=self.load_preset).pack(
            side="left", padx=10
        )

        # Timer logic
        self.timer = CountdownTimer(self.ws)

        # Timer controls
        ttk.Label(master, text="Timer (minutes):").pack(pady=(5, 0))
        self.timer_entry = ttk.Entry(master)
        self.timer_entry.insert(0, "5")
        self.timer_entry.pack(fill="x", padx=20)

        self.timer_state = tk.StringVar(value="stopped")

        timer_button_frame = ttk.Frame(master)
        timer_button_frame.pack(pady=(10, 15))

        self.start_pause_button = ttk.Button(
            timer_button_frame, text="Start", command=self.toggle_timer
        )
        self.start_pause_button.pack(side="left", padx=5)

        ttk.Button(timer_button_frame, text="Reset", command=self.reset_timer).pack(
            side="left", padx=5
        )

        self.clock = Clock(self.ws)
        self.clock.play()

    def apply_changes(self):
        try:
            # Highlight Team
            selected_team = self.team_var.get()
            team_index = self.school_dropdown_options.index(selected_team) - 1
            lineup.set_highlight(team_index, self.ws)

            # Camera Mode
            if self.mode_var.get() == "full":
                selected = self.cam_vars[0].get()
                cam_index = (
                    -1 if selected == "Off" else self.camera_names.index(selected)
                )
                cameras.set_full_cam(cam_index, self.ws)
            else:
                cam_indices = [
                    -1 if var.get() == "Off" else self.camera_names.index(var.get())
                    for var in self.cam_vars
                ]
                cameras.set_split_cam(self.ws, cam_indices)

            print("✅ Applied successfully.")
        except Exception as e:
            print(f"❌ Error applying changes: {e}")

    def save_preset(self):
        preset_name = self.preset_var.get().replace(" ", "_").lower()
        path = os.path.join(PRESET_FOLDER, f"{preset_name}.json")

        preset_data = {
            "team": self.team_var.get(),
            "mode": self.mode_var.get(),
            "cameras": [var.get() for var in self.cam_vars],
        }

        try:
            with open(path, "w") as f:
                json.dump(preset_data, f, indent=2)
            print(f"💾 Preset saved to {path}")
        except Exception as e:
            print(f"❌ Failed to save preset: {e}")

    def load_preset(self):
        preset_name = self.preset_var.get().replace(" ", "_").lower()
        path = os.path.join(PRESET_FOLDER, f"{preset_name}.json")

        if not os.path.exists(path):
            print(f"⚠️ Preset file does not exist: {path}")
            return

        try:
            with open(path, "r") as f:
                preset_data = json.load(f)

            # Load values
            if preset_data["team"] in self.school_dropdown_options:
                self.team_var.set(preset_data["team"])

            self.mode_var.set(preset_data["mode"])

            for i, name in enumerate(preset_data["cameras"]):
                if name in self.cam_dropdown_options:
                    self.cam_vars[i].set(name)

            print(f"✅ Preset loaded from {path}")
        except Exception as e:
            print(f"❌ Failed to load preset: {e}")

    def toggle_timer(self):
        state = self.timer_state.get()

        if state == "running":
            self.timer.pause()
            self.timer_state.set("paused")
            self.start_pause_button.config(text="Resume")
        elif state == "paused":
            self.timer.play()
            self.timer_state.set("running")
            self.start_pause_button.config(text="Pause")

    def reset_timer(self):
        try:
            self.timer_state.set("paused")
            minutes = float(self.timer_entry.get())
            self.timer.set_time(minutes)
            self.start_pause_button.config(text="Start")
        except ValueError:
            print("⚠️ Invalid timer value.")


def run_gui():
    root = tk.Tk()
    app = OBSControlGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
