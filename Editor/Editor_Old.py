import struct
import os
from tkinter import Tk, filedialog, Label, Button, Entry, messagebox

# Global constants
START_OFFSET = 0x120
STEP = 0x30
NUM_SENSORS = 20
SENSOR_DATA_SIZE = 24  # 6 floats * 4 bytes each

DEFAULT_SENSOR_VALUE = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
SENSOR_POSITIONS = [
    "roof_upper_left", "roof_upper_right", "roof_lower_right", "roof_lower_left", "front_lower_right",
    "front_upper_right", "front_lower_middle", "front_upper_middle", "front_lower_left", "front_upper_left",
    "door_back_left", "door_front_left", "door_back_right", "door_front_right", "back_lower_right",
    "back_upper_right", "back_lower_middle", "back_upper_middle", "back_lower_left", "back_upper_left"
]

def read_sensor_data(filepath):
    sensors = []
    try:
        with open(filepath, "rb") as f:
            for i in range(NUM_SENSORS):
                offset = START_OFFSET + i * (STEP + 0x10)
                f.seek(offset)
                data = f.read(SENSOR_DATA_SIZE)
                sensors.append(struct.unpack(">6f", data))
        return sensors
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None

def write_sensor_data(filepath, sensors):
    try:
        with open(filepath, "r+b") as f:
            for i, sensor in enumerate(sensors):
                offset = START_OFFSET + i * (STEP + 0x10)
                f.seek(offset)
                f.write(struct.pack(">6f", *sensor))
        return True
    except Exception as e:
        print(f"Error writing file {filepath}: {e}")
        return False

class SensorEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Sensor Data Editor")
        self.root.geometry("700x900")
        
        self.current_filepath = ""
        self.batch_files = []
        self.entries = []
        self.sensors = []
        self.original_sensors = []

        # Create UI elements
        self.create_controls()
        self.batch_controls_visible(False)
        self.single_file_controls_visible(False)

    def create_controls(self):
        # Top controls
        Button(self.root, text="Open File", command=self.open_file).grid(row=0, column=0, padx=5, pady=5)
        Button(self.root, text="Open Folder", command=self.open_folder).grid(row=0, column=1, padx=5, pady=5)

        # Batch controls
        self.batch_multiplier_label = Label(self.root, text="Batch Multiplier:")
        self.batch_multiplier_entry = Entry(self.root, width=10)
        self.batch_apply_btn = Button(self.root, text="Apply to All Files", command=self.batch_apply_multiplier)

        # Single file controls (initially hidden)
        self.single_multiplier_label = Label(self.root, text="Multiply Factor:")
        self.single_multiplier_entry = Entry(self.root, width=10)
        self.single_apply_btn = Button(self.root, text="Apply", command=self.apply_single_multiplier)
        self.reset_all_btn = Button(self.root, text="Reset All", command=self.reset_all)
        self.save_btn = Button(self.root, text="Save", command=self.save_file)

    def batch_controls_visible(self, visible):
        if visible:
            self.batch_multiplier_label.grid(row=1, column=0, padx=5, pady=5)
            self.batch_multiplier_entry.grid(row=1, column=1, padx=5, pady=5)
            self.batch_apply_btn.grid(row=1, column=2, padx=5, pady=5)
        else:
            self.batch_multiplier_label.grid_remove()
            self.batch_multiplier_entry.grid_remove()
            self.batch_apply_btn.grid_remove()

    def single_file_controls_visible(self, visible):
        if visible:
            self.single_multiplier_label.grid(row=25, column=0, padx=5, pady=5)
            self.single_multiplier_entry.grid(row=25, column=1, padx=5, pady=5)
            self.single_apply_btn.grid(row=25, column=2, padx=5, pady=5)
            self.reset_all_btn.grid(row=24, column=0, pady=5)
            self.save_btn.grid(row=24, column=1, pady=5)
        else:
            self.single_multiplier_label.grid_remove()
            self.single_multiplier_entry.grid_remove()
            self.single_apply_btn.grid_remove()
            self.reset_all_btn.grid_remove()
            self.save_btn.grid_remove()

    def clear_sensor_widgets(self):
        for widget in self.root.grid_slaves():
            if widget.grid_info()["row"] > 3 and widget not in [
                self.single_multiplier_label, self.single_multiplier_entry, 
                self.single_apply_btn, self.reset_all_btn, self.save_btn
            ]:
                widget.destroy()
        self.entries = []

    def open_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("DAT/BIN files", "*.dat *.DAT *.bin *.BIN")])
        if filepath:
            self.process_single_file(filepath)
            self.batch_controls_visible(False)
            self.single_file_controls_visible(True)

    def open_folder(self):
        folderpath = filedialog.askdirectory(title="Select Root Folder")
        if not folderpath:
            return
        
        self.batch_files = []
        for root_dir, dirs, files in os.walk(folderpath):
            if "StreamedDeformationSpec" in dirs:
                spec_dir = os.path.join(root_dir, "StreamedDeformationSpec")
                for file in os.listdir(spec_dir):
                    if file.lower().endswith(('.dat', '.bin')):
                        self.batch_files.append(os.path.join(spec_dir, file))
        
        self.clear_sensor_widgets()
        self.single_file_controls_visible(False)
        self.batch_controls_visible(True)
        messagebox.showinfo("Files Found", f"Found {len(self.batch_files)} StreamedDeformationSpec files")

    def process_single_file(self, filepath):
        self.current_filepath = filepath
        self.clear_sensor_widgets()
        
        sensors = read_sensor_data(filepath)
        if not sensors:
            return

        self.sensors = sensors
        self.original_sensors = [list(s) for s in sensors]
        
        for r in range(NUM_SENSORS):
            Label(self.root, text=SENSOR_POSITIONS[r], width=15, anchor="w").grid(row=r+4, column=0, padx=5, pady=3)
            row_entries = []
            for c in range(6):
                e = Entry(self.root, width=10)
                e.grid(row=r+4, column=c+1, padx=5, pady=3)
                e.insert(0, f"{self.sensors[r][c]:.4f}")
                row_entries.append(e)
            self.entries.append(row_entries)
            Button(self.root, text="Reset", command=lambda rr=r: self.reset_single_sensor(rr)).grid(row=r+4, column=7, padx=5, pady=3)

    def reset_single_sensor(self, row):
        for c in range(6):
            self.entries[row][c].delete(0, "end")
            self.entries[row][c].insert(0, f"{self.original_sensors[row][c]:.4f}")

    def reset_all(self):
        for r in range(20):
            for c in range(6):
                self.entries[r][c].delete(0, "end")
                self.entries[r][c].insert(0, f"{self.original_sensors[r][c]:.4f}")

    def save_file(self):
        for r in range(NUM_SENSORS):
            self.sensors[r] = tuple(float(self.entries[r][c].get()) for c in range(6))
        if write_sensor_data(self.current_filepath, self.sensors):
            messagebox.showinfo("Saved", "All changes saved to file")

    def apply_single_multiplier(self):
        try:
            factor = float(self.single_multiplier_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid multiplier")
            return

        for r in range(20):
            for c in range(6):
                entry = self.entries[r][c]
                current_value = float(entry.get())
                entry.delete(0, "end")
                entry.insert(0, f"{current_value * factor:.4f}")

    def batch_apply_multiplier(self):
        if not self.batch_files:
            messagebox.showwarning("No Files", "Select a folder first")
            return

        try:
            multiplier = float(self.batch_multiplier_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid multiplier")
            return

        success = 0
        for filepath in self.batch_files:
            sensors = read_sensor_data(filepath)
            if not sensors:
                continue
            
            modified = [tuple(val * multiplier for val in s) for s in sensors]
            if write_sensor_data(filepath, modified):
                success += 1

            if filepath == self.current_filepath:
                self.process_single_file(filepath)

        messagebox.showinfo("Complete", f"Processed {len(self.batch_files)} files\nSuccess: {success}")

if __name__ == "__main__":
    root = Tk()
    app = SensorEditor(root)
    root.mainloop()
