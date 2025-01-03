import struct
import os
from tkinter import Tk, filedialog, Toplevel, Label, Button, Entry, messagebox
import pandas as pd
from tabulate import tabulate

DEFAULT_SENSOR_VALUE = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
SENSOR_POSITIONS = [
    "roof_upper_left", "roof_upper_right", "roof_lower_right", "roof_lower_left", "front_lower_right",
    "front_upper_right", "front_lower_middle", "front_upper_middle", "front_lower_left", "front_upper_left",
    "door_back_left", "door_front_left", "door_back_right", "door_front_right", "back_lower_right",
    "back_upper_right", "back_lower_middle", "back_upper_middle", "back_lower_left", "back_upper_left"
]

def read_sensor_data(filepath, start_offset, step, num_sensors=20):
    """Reads sensor data from the .dat file."""
    sensors = []
    try:
        with open(filepath, "rb") as f:
            for i in range(num_sensors):
                offset = start_offset + i * (step + 0x10)  # Includes padding correction
                f.seek(offset)
                # Read 6 floats (6 * 4 bytes = 24 bytes)
                data = f.read(24)
                sensors.append(struct.unpack(">6f", data))
        return sensors
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

def write_sensor_data(filepath, start_offset, step, sensors):
    """Writes sensor data back to the .dat file."""
    try:
        with open(filepath, "r+b") as f:
            for i, sensor in enumerate(sensors):
                offset = start_offset + i * (step + 0x10)
                f.seek(offset)
                # Write 6 floats as big-endian
                f.write(struct.pack(">6f", *sensor))
        print(f"Successfully updated {filepath}")
    except Exception as e:
        print(f"Error writing file: {e}")

def display_sensors_table(sensors):
    """Displays the sensor data in a table format."""
    df = pd.DataFrame(sensors, columns=["Value 1", "Value 2", "Value 3", "Value 4", "Value 5", "Value 6"])
    df["Position"] = SENSOR_POSITIONS
    df.index.name = "Sensor ID"
    print(tabulate(df, headers="keys", tablefmt="pretty"))

def main():
    root = Tk()
    root.title("Sensor Data Editor")
    root.geometry("700x750")

    # Add an icon to the window
    # icon_path = "icon.ico"
    # if os.path.exists(icon_path):
    #     root.iconbitmap(icon_path)

    original_sensors = []
    sensors = []
    entries = []  # 20 sensors x 6 values

    def open_file():
        nonlocal sensors, original_sensors
        filepath = filedialog.askopenfilename(
            title="Select .bin file",
            filetypes=[("BIN files", "*.bin"), ("All files", "*.*")],
        )
        if not filepath:
            return
        # Read data
        num_sensors = 20
        start_offset = 0x120
        step = 0x30
        sensors = read_sensor_data(filepath, start_offset, step, num_sensors)
        original_sensors = [list(s) for s in sensors]
        show_sensors_table(filepath, start_offset, step)

    def show_sensors_table(filepath, start_offset, step):
        # Clear old widgets except open_file_btn
        for widget in root.grid_slaves():
            if widget != open_file_btn:
                widget.destroy()

        # Draw sensor table starting from row=1
        for r in range(20):
            Label(root, text=SENSOR_POSITIONS[r], width=15, anchor="w").grid(row=r+1, column=0, padx=5, pady=3)
            row_entries = []
            for c in range(6):
                e = Entry(root, width=10)
                e.grid(row=r+1, column=c+1, padx=5, pady=3)
                e.insert(0, f"{sensors[r][c]:.4f}")  # Display with 4 decimals
                row_entries.append(e)
            entries.append(row_entries)

            def make_reset_sensor(rr=r):
                def reset_sensor():
                    for c2 in range(6):
                        entries[rr][c2].delete(0, "end")
                        entries[rr][c2].insert(0, f"{original_sensors[rr][c2]:.4f}")
                return reset_sensor
            Button(root, text="Reset", command=make_reset_sensor()).grid(row=r+1, column=7, padx=5, pady=3)

        # Buttons row at row=22
        Button(root, text="Reset All", command=reset_all).grid(row=22, column=0, pady=5)

        def save():
            for r in range(20):
                sensors[r] = tuple(float(entries[r][c].get()) for c in range(6))
            write_sensor_data(filepath, start_offset, step, sensors)
            messagebox.showinfo("Saved", "All changes saved to file.")

        Button(root, text="Save", command=save).grid(row=22, column=1, pady=5)

    def reset_all():
        for r in range(20):
            for c in range(6):
                entries[r][c].delete(0, "end")
                entries[r][c].insert(0, f"{original_sensors[r][c]:.3f}")

    open_file_btn = Button(root, text="Open File", command=open_file)
    open_file_btn.grid(row=0, column=0, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
