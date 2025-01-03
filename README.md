# Burnout_AT_Editor

Burnout_AT_Editor is a tool designed to edit the StreamedDeformationSpec of Burnout Paradise cars, allowing you to modify sensor data related to car deformation within the game.

## Features

- **Read and Display Sensor Data:** Easily access sensor data from `.bin` files extracted from the AT files of Burnout Paradise cars.
- **Graphical Interface:** Intuitive GUI for editing sensor values.
- **Reset Sensors:** Restore individual sensors or all sensors to their values when you opened the file.
- **Save Changes:** Apply and save your modifications back to the `.bin` files.

## Requirements

- **Python 3.x**
- **pandas**
- **tabulate**
- **tkinter**

```bash	
pip install pandas tabulate tkinter
```

## Usage

1. **Run the application:**
   
   ```bash
   python main.py
   ```

2. **Open a `.bin` file:**
   - Click on the "Open File" button and select your Burnout Paradise car `.bin` file.

3. **Edit sensor values:**
   - Use the graphical interface to modify sensor data as desired.

4. **Save your changes:**
   - Click on the "Save" button to write the changes back to the `.bin` file.