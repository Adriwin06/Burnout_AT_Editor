import os
import copy
import customtkinter
from tkinter import filedialog, messagebox
from sensor_io import read_sensor_data, write_sensor_data, SENSOR_POSITIONS, NUM_SENSORS
from data import car_name

class SensorEditor:
    def __init__(self, root):
        """Initialize the SensorEditor with main window setup and initial variables."""
        self.root = root
        self.root.title("Sensor Data Editor")
        self.root.geometry("1400x800")
        
        # Configure grid weights for better responsiveness.
        # Row 0: Top controls, Row 1: Folder batch controls, Row 2: Sensor detail (left/right), Row 3: Bottom controls.
        self.root.grid_columnconfigure(1, weight=3)  # Main content gets more space
        self.root.grid_columnconfigure(0, weight=1)  # Sidebar gets less space
        self.root.grid_rowconfigure(2, weight=1)     # Sensor detail area expands

        self.current_filepath = ""
        self.batch_files = []
        self.modified_sensors = {}  # Dictionary to track unsaved changes
        self.sensors = []
        self.original_sensors = []
        self.current_sensor_index = 0
        self.sensor_entries = {}
        self.sensor_buttons = []

        self.create_controls()
        self.create_bottom_controls()
        self.batch_controls_visible(False)
        self.sensor_detail_visible(False)
        
    def create_controls(self):
        """Create and layout the main UI controls (top bar, left sidebar, sensor detail area)."""
        # Top bar
        top_frame = customtkinter.CTkFrame(self.root)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(10,5))
        top_frame.grid_columnconfigure(3, weight=1)  # Ensure it stretches

        self.open_file_btn = customtkinter.CTkButton(top_frame, text="Open File", command=self.open_file, width=120)
        self.open_file_btn.grid(row=0, column=0, padx=(10,5), pady=5)

        self.open_folder_btn = customtkinter.CTkButton(top_frame, text="Open Folder", command=self.open_folder, width=120)
        self.open_folder_btn.grid(row=0, column=1, padx=5, pady=5)

        self.car_name_label = customtkinter.CTkLabel(top_frame, text="", font=("Arial", 14), anchor="w")
        self.car_name_label.grid(row=0, column=3, padx=10, pady=5, sticky="e")

        # Batch controls container
        self.batch_frame = customtkinter.CTkFrame(self.root)
        self.batch_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=5)
        self.batch_frame.grid_columnconfigure(1, weight=1)

        self.batch_multiplier_label = customtkinter.CTkLabel(self.batch_frame, text="Batch Sensors' Direction Params Multiplier:", anchor="w")
        self.batch_multiplier_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.batch_multiplier_entry = customtkinter.CTkEntry(self.batch_frame, width=120)
        self.batch_multiplier_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.batch_apply_btn = customtkinter.CTkButton(self.batch_frame, text="Apply to All Files", 
                                                    command=self.batch_apply_multiplier, width=120)
        self.batch_apply_btn.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Left sidebar
        self.left_frame = customtkinter.CTkFrame(self.root)
        self.left_frame.grid(row=2, column=0, sticky="nsw", padx=20, pady=(5,10))
        self.left_frame.grid_rowconfigure(0, weight=1)

        self.sensor_scrollable_frame = customtkinter.CTkScrollableFrame(self.left_frame, width=280)
        self.sensor_scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        # Right content area
        self.right_frame = customtkinter.CTkFrame(self.root)
        self.right_frame.grid(row=2, column=1, sticky="nsew", padx=(0,20), pady=(5,10))
        self.right_frame.grid_columnconfigure(1, weight=1)
        
    def create_bottom_controls(self):
        """Create the bottom row that holds the batch multiplier for all sensors and the Save File button.
        
        The batch multiplier controls are aligned to the left and the Save File button is aligned to the right.
        """
        self.bottom_frame = customtkinter.CTkFrame(self.root)
        self.bottom_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=(10,20))
        self.bottom_frame.grid_columnconfigure(0, weight=1)  # Left group expands
        
        # Left group: Batch multiplier controls
        left_group = customtkinter.CTkFrame(self.bottom_frame)
        left_group.grid(row=0, column=0, sticky="w")
        
        bottom_label = customtkinter.CTkLabel(left_group, text="Batch Multiply All Sensors' Direction Params by:")
        bottom_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.batch_multiplier_all_entry = customtkinter.CTkEntry(left_group, width=100)
        self.batch_multiplier_all_entry.grid(row=0, column=1, padx=5, pady=5)
        
        bottom_batch_btn = customtkinter.CTkButton(left_group, text="Apply to All Sensors", 
                                                   command=self.batch_multiply_all_sensors)
        bottom_batch_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Right group: Save File button
        save_file_btn = customtkinter.CTkButton(self.bottom_frame, text="Save File", command=self.save_file, width=120)
        save_file_btn.grid(row=0, column=1, sticky="e", padx=20, pady=5)
        
    def batch_controls_visible(self, visible):
        """Toggle visibility of folder batch processing controls."""
        if visible:
            self.batch_frame.grid()
        else:
            self.batch_frame.grid_remove()
            
    def sensor_detail_visible(self, visible):
        """Toggle visibility of the sensor detail panels and the bottom controls.
        
        Args:
            visible (bool): Whether to show or hide sensor details.
        """
        if visible:
            self.left_frame.grid()
            self.right_frame.grid()
            self.bottom_frame.grid()
        else:
            self.left_frame.grid_remove()
            self.right_frame.grid_remove()
            self.bottom_frame.grid_remove()
            
    def clear_sensor_detail(self):
        """Clear all sensor detail widgets from the right frame."""
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        self.sensor_entries = {}
        
    def load_sensor_list(self):
        """Create and populate the list of sensor buttons in the left panel."""
        for widget in self.sensor_scrollable_frame.winfo_children():
            widget.destroy()
        self.sensor_buttons = []
        for index, sensor_name in enumerate(SENSOR_POSITIONS):
            btn = customtkinter.CTkButton(self.sensor_scrollable_frame, text=sensor_name,
                                          command=lambda i=index: self.on_sensor_select(i),
                                          width=250, height=35,
                                          fg_color=("gray75", "gray30"))  # Default unselected color
            btn.grid(row=index, column=0, pady=(0,5), padx=5, sticky="ew")
            self.sensor_buttons.append(btn)
        if self.sensor_buttons:
            self.sensor_buttons[0].configure(fg_color=customtkinter.ThemeManager.theme["CTkButton"]["fg_color"])
            self.current_sensor_index = 0
        
    def update_sensor_buttons(self):
        """Update the visual state of sensor buttons, highlighting the selected one."""
        for i, btn in enumerate(self.sensor_buttons):
            btn.configure(fg_color=customtkinter.ThemeManager.theme["CTkButton"]["fg_color"] 
                          if i == self.current_sensor_index else ("gray75", "gray30"))
                
    def load_sensor_details(self, index):
        """Load and display all details for the selected sensor.
        
        Args:
            index (int): Index of the sensor to display.
        """
        self.clear_sensor_detail()
        
        # Use modified sensor if available, otherwise the original sensor data.
        sensor = self.modified_sensors.get(index, self.sensors[index])

        # Entry width constant for uniformity.
        ENTRY_WIDTH = 100

        # Title section
        title_frame = customtkinter.CTkFrame(self.right_frame)
        title_frame.grid(row=0, column=0, columnspan=7, sticky="ew", padx=20, pady=10)
        title = customtkinter.CTkLabel(title_frame,
                                       text=f"Sensor: {SENSOR_POSITIONS[index]} (Index {index})",
                                       font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # Main content frame for sensor details
        content_frame = customtkinter.CTkFrame(self.right_frame)
        content_frame.grid(row=1, column=0, columnspan=7, sticky="nsew", padx=20, pady=10)

        # Helper function to create a row of entry fields.
        def create_field_group(parent, row, label_text, values, entry_count):
            label = customtkinter.CTkLabel(parent, text=label_text, anchor="w")
            label.grid(row=row, column=0, sticky="w", padx=10, pady=5)
            entries = []
            for i in range(entry_count):
                entry = customtkinter.CTkEntry(parent, width=ENTRY_WIDTH)
                entry.grid(row=row, column=i+1, padx=5, pady=5)
                entry.insert(0, f"{values[i]}")
                entries.append(entry)
            return entries

        current_row = 0

        # Direction Parameters (6 floats)
        self.sensor_entries["maDirectionParams"] = create_field_group(
            content_frame, current_row,
            "maDirectionParams:", 
            [f"{x:.4f}" for x in sensor["maDirectionParams"]], 
            6
        )
        current_row += 1

        # Radius (float)
        self.sensor_entries["mfRadius"] = create_field_group(
            content_frame, current_row,
            "mfRadius:", 
            [f"{sensor['mfRadius']:.4f}"], 
            1
        )[0]
        current_row += 1

        # Next Sensor (6 uint8)
        self.sensor_entries["maNextSensor"] = create_field_group(
            content_frame, current_row,
            "maNextSensor:", 
            sensor["maNextSensor"], 
            6
        )
        current_row += 1

        # Scene Index (uint8)
        self.sensor_entries["mu8SceneIndex"] = create_field_group(
            content_frame, current_row,
            "mu8SceneIndex:", 
            [sensor["mu8SceneIndex"]], 
            1
        )[0]
        current_row += 1

        # Absorbtion Level (uint8)
        self.sensor_entries["mu8AbsorbtionLevel"] = create_field_group(
            content_frame, current_row,
            "mu8AbsorbtionLevel:", 
            [sensor["mu8AbsorbtionLevel"]], 
            1
        )[0]
        current_row += 1

        # Next Boundary Sensor (2 uint8)
        self.sensor_entries["mau8NextBoundarySensor"] = create_field_group(
            content_frame, current_row,
            "mau8NextBoundarySensor:", 
            sensor["mau8NextBoundarySensor"], 
            2
        )
        current_row += 1

        # Multiplier section for the current sensor only
        multiplier_frame = customtkinter.CTkFrame(content_frame)
        multiplier_frame.grid(row=current_row, column=0, columnspan=7, sticky="ew", pady=15)
        lbl_mult = customtkinter.CTkLabel(multiplier_frame, text="Multiply Current Sensor Direction Params by:")
        lbl_mult.grid(row=0, column=0, padx=10, pady=5)
        self.multiplier_entry = customtkinter.CTkEntry(multiplier_frame, width=ENTRY_WIDTH)
        self.multiplier_entry.grid(row=0, column=1, padx=5, pady=5)
        mult_btn = customtkinter.CTkButton(multiplier_frame, text="Apply", command=self.multiply_floats)
        mult_btn.grid(row=0, column=2, padx=5, pady=5)
        current_row += 1

        # Sensor-specific buttons (affect only the current sensor)
        sensor_button_frame = customtkinter.CTkFrame(content_frame)
        sensor_button_frame.grid(row=current_row, column=0, columnspan=7, sticky="ew", pady=15)
        buttons = [
            ("< Previous Sensor", self.prev_sensor),
            ("Reset Sensor", self.reset_sensor),
            ("Save Sensor", self.save_sensor),
            ("Next Sensor >", self.next_sensor)
        ]
        for i, (text, command) in enumerate(buttons):
            btn = customtkinter.CTkButton(sensor_button_frame, text=text, command=command, width=120)
            btn.grid(row=0, column=i, padx=10, pady=10)
        
    def store_current_sensor_changes(self):
        """Store current sensor entry values into modified_sensors (in memory only)."""
        if not self.sensor_entries:
            return
        try:
            sensor = {
                "maDirectionParams": tuple(float(e.get()) for e in self.sensor_entries["maDirectionParams"]),
                "mfRadius": float(self.sensor_entries["mfRadius"].get()),
                "maNextSensor": tuple(int(e.get()) for e in self.sensor_entries["maNextSensor"]),
                "mu8SceneIndex": int(self.sensor_entries["mu8SceneIndex"].get()),
                "mu8AbsorbtionLevel": int(self.sensor_entries["mu8AbsorbtionLevel"].get()),
                "mau8NextBoundarySensor": tuple(int(e.get()) for e in self.sensor_entries["mau8NextBoundarySensor"])
            }
        except Exception as e:
            print(f"Error storing current sensor changes: {e}")
            return
        self.modified_sensors[self.current_sensor_index] = sensor
        
    def on_sensor_select(self, index):
        """Handle sensor selection from the list.
        
        Args:
            index (int): Index of the selected sensor.
        """
        # Before switching, store any changes made in the current sensor's entries.
        if self.sensor_entries:
            self.store_current_sensor_changes()
        self.current_sensor_index = index
        self.update_sensor_buttons()
        self.load_sensor_details(index)
        
    def reset_sensor(self):
        """Reset current sensor values to their original state."""
        self.modified_sensors.pop(self.current_sensor_index, None)
        sensor = self.original_sensors[self.current_sensor_index]
        for i, e in enumerate(self.sensor_entries["maDirectionParams"]):
            e.delete(0, customtkinter.END)
            e.insert(0, f"{sensor['maDirectionParams'][i]:.4f}")
        self.sensor_entries["mfRadius"].delete(0, customtkinter.END)
        self.sensor_entries["mfRadius"].insert(0, f"{sensor['mfRadius']:.4f}")
        for i, e in enumerate(self.sensor_entries["maNextSensor"]):
            e.delete(0, customtkinter.END)
            e.insert(0, f"{sensor['maNextSensor'][i]}")
        self.sensor_entries["mu8SceneIndex"].delete(0, customtkinter.END)
        self.sensor_entries["mu8SceneIndex"].insert(0, f"{sensor['mu8SceneIndex']}")
        self.sensor_entries["mu8AbsorbtionLevel"].delete(0, customtkinter.END)
        self.sensor_entries["mu8AbsorbtionLevel"].insert(0, f"{sensor['mu8AbsorbtionLevel']}")
        for i, e in enumerate(self.sensor_entries["mau8NextBoundarySensor"]):
            e.delete(0, customtkinter.END)
            e.insert(0, f"{sensor['mau8NextBoundarySensor'][i]}")
            
    def save_sensor(self):
        """Save current sensor values to memory (without writing to file)."""
        try:
            sensor = {
                "maDirectionParams": tuple(float(e.get()) for e in self.sensor_entries["maDirectionParams"]),
                "mfRadius": float(self.sensor_entries["mfRadius"].get()),
                "maNextSensor": tuple(int(e.get()) for e in self.sensor_entries["maNextSensor"]),
                "mu8SceneIndex": int(self.sensor_entries["mu8SceneIndex"].get()),
                "mu8AbsorbtionLevel": int(self.sensor_entries["mu8AbsorbtionLevel"].get()),
                "mau8NextBoundarySensor": tuple(int(e.get()) for e in self.sensor_entries["mau8NextBoundarySensor"])
            }
        except Exception as e:
            messagebox.showerror("Error", f"Invalid data: {e}")
            return
        self.modified_sensors[self.current_sensor_index] = sensor
        messagebox.showinfo("Saved", f"Sensor {SENSOR_POSITIONS[self.current_sensor_index]} updated in memory.")
        
    def multiply_floats(self):
        """Multiply the direction parameters of the current sensor by the specified multiplier."""
        try:
            factor = float(self.multiplier_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid multiplier")
            return
        for e in self.sensor_entries["maDirectionParams"]:
            try:
                val = float(e.get())
                e.delete(0, customtkinter.END)
                e.insert(0, f"{val * factor:.4f}")
            except ValueError:
                continue
        
    def batch_multiply_all_sensors(self):
        """Multiply the direction parameters for all sensors in the opened file by the specified multiplier."""
        try:
            factor = float(self.batch_multiplier_all_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid multiplier for batch operation")
            return
        
        # Apply multiplication to every sensor (using modified version if available)
        for i in range(len(self.sensors)):
            sensor = self.modified_sensors.get(i, self.sensors[i])
            try:
                new_direction_params = tuple(val * factor for val in sensor["maDirectionParams"])
            except Exception as e:
                print(f"Error multiplying sensor {i} direction params: {e}")
                continue
            new_sensor = dict(sensor)
            new_sensor["maDirectionParams"] = new_direction_params
            self.modified_sensors[i] = new_sensor
        messagebox.showinfo("Success", "Batch multiplication applied to all sensors (in memory).")
        self.load_sensor_details(self.current_sensor_index)
        
    def prev_sensor(self):
        """Navigate to the previous sensor in the list."""
        idx = self.current_sensor_index - 1 if self.current_sensor_index - 1 >= 0 else NUM_SENSORS - 1
        self.on_sensor_select(idx)
        
    def next_sensor(self):
        """Navigate to the next sensor in the list."""
        idx = (self.current_sensor_index + 1) % NUM_SENSORS
        self.on_sensor_select(idx)
        
    def save_file(self):
        """Write all in-memory sensor changes to the current file."""
        self.save_sensor()  # Save current sensor first
        for idx, modified_sensor in self.modified_sensors.items():
            self.sensors[idx] = modified_sensor
        if write_sensor_data(self.current_filepath, self.sensors):
            messagebox.showinfo("Saved", "All changes saved to file")
            self.modified_sensors.clear()
        else:
            messagebox.showerror("Error", "Failed to save file")
        
    def open_file(self):
        """Open a file dialog and load the selected sensor file."""
        filepath = filedialog.askopenfilename(filetypes=[("DAT/BIN files", "*.dat *.DAT *.bin *.BIN")])
        if filepath:
            self.process_single_file(filepath)
            self.batch_controls_visible(False)
            self.sensor_detail_visible(True)
            self.update_car_name_label(filepath)
        
    def open_folder(self):
        """Open a folder dialog and find all sensor files for batch processing."""
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
        self.sensor_detail_visible(False)
        self.batch_controls_visible(True)
        messagebox.showinfo("Files Found", f"Found {len(self.batch_files)} StreamedDeformationSpec files")
        self.car_name_label.configure(text=f"Editing {len(self.batch_files)} StreamedDeformationSpec files in {folderpath}.")

    def update_car_name_label(self, filepath):
        """Update the car name label based on the file path."""
        parts = filepath.split('/')
        car_id = next((part.split('_')[1] for part in parts if 'VEH_' in part and '_' in part), None)

        if car_id and car_id.endswith("BIN"):
            car_id = car_id[:-3]

        if car_id and car_id in car_name:
            self.car_name_label.configure(text=f"Car: {car_name[car_id]}")
        else:
            filename = os.path.basename(filepath)
            self.car_name_label.configure(text=f"File: {filename}")
        
    def process_single_file(self, filepath):
        """Load and process a single sensor file.
        
        Args:
            filepath (str): Path to the sensor file.
        """
        self.current_filepath = filepath
        self.modified_sensors.clear()
        sensors = read_sensor_data(filepath)
        if not sensors:
            messagebox.showerror("Error", "Failed to read sensor data from file.")
            return
        self.sensors = sensors
        self.original_sensors = copy.deepcopy(sensors)
        self.load_sensor_list()
        self.load_sensor_details(0)
        
    def batch_apply_multiplier(self):
        """Apply multiplier to sensor directions in all files in batch mode (folder batch processing)."""
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
            modified_sensors = []
            for sensor in sensors:
                sensor["maDirectionParams"] = tuple(val * multiplier for val in sensor["maDirectionParams"])
                # mfRadius remains unchanged.
                modified_sensors.append(sensor)
            if write_sensor_data(filepath, modified_sensors):
                success += 1
            if filepath == self.current_filepath:
                self.process_single_file(filepath)
        messagebox.showinfo("Complete", f"Processed {len(self.batch_files)} files\nSuccess: {success}")
