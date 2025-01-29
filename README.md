# Burnout Paradise AT Editor

## Installation
You can either download the latest release from the [Releases](https://github.com/Adriwin06/Burnout_AT_Editor/releases) but it might be outdated or you can clone the repository and run it with Python.

## Prerequisites

### 1. YAP Tool (Required for Batch Files)
**You must download these files first:**  
🔗 [Download YAP from GitHub](https://github.com/burninrubber0/YAP/releases)  
*(Credit to burninrubber0 for the incredible tool, as always)*

**After downloading:**
1. Extract these files where the batch files are:
   - `yap.exe`
   - `Qt6Core.dll`
2. Place the batch files (`extract_vehicles.bat` and `repack_vehicles.bat`) in the **same folder** as YAP

### 2. Python Requirements
```bash
pip install pandas tabulate
```

## Setup Guide

1. **Folder Structure**  
   Create this structure (❗ YAP files and batch files must be together):
   ```
   Burnout_AT_Toolkit/
   ├── yap.exe          # From YAP download
   ├── Qt6Core.dll      # From YAP download
   ├── extract_vehicles.bat
   ├── repack_vehicles.bat
   └── Burnout_AT_Editor/
       ├── main.py
       └── (other python files)
   ```

2. **Game Files Backup**  
   Always keep a copy of your original `VEHICLES` folder!

---

## Workflow

### 1. Extract Bundles
```bash
Run extract_vehicles.bat
➜ Source: Game's VEHICLES/AT folder
➜ Destination: Create new folder (e.g., MyMods/Extracted)
```

### 2. Edit Sensors Values from StreamedDeformationSpecs files
```bash
1. Run the tool
2. You can select a specific vehicle or the whole folder that contains extracted files
⚠️ If you select the folder, you will only be able to multiply the values by a factor.
3. Modify values & save
```

### 3. Repack Bundles
```bash
Run repack_vehicles.bat
➜ Source: MyMods/Extracted
➜ Destination: Create MyMods/Repacked
```

### 4. Install Modified Files
Copy all `.BIN` files from `Repacked` to the game's `VEHICLES` folder

---

## ❗ Important Notes
- Without YAP files, the batch scripts **will not work**
- YAP handles the actual bundle extraction/repacking
- the editor only modifies values in extracted StreamedDeformationSpecs files