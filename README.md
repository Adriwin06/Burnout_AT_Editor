# Burnout Paradise AT Editor

## Installation
Download the latest release from the [Releases](https://github.com/Adriwin06/Burnout_AT_Editor/releases) page or clone the repository and run it with Python.

## Prerequisites

### 1. YAP Tool (for bundle extraction/repacking)
Download YAP from GitHub:  
🔗 [Download YAP](https://github.com/burninrubber0/YAP/releases/tag/v0.2-directory)  
Extract and run it via:
```bash
./YAP.exe
```

### 2. Python Dependencies
```bash
pip install pandas tabulate customtkinter tkinter
```

## Workflow

1. **Extract Bundles**  
   Use YAP to extract bundles from your game files:
   ```bash
   YAP e <input bundle> <output folder>
   ```
   (More details in the [YAP README](https://github.com/burninrubber0/YAP/tree/directory?tab=readme-ov-file#extracting-multiple-bundles))
2. **Edit Sensor Values**  
   Launch the editor tool to adjust sensor parameters. You can modify:
   - **maDirectionParams**: Controls the maximum distance each sensor can go in a specific direction.
   - **mfRadius**: Control the size of the sensor/the area of the car it covers.
   - **maNextSensor**: All the surrounding sensors.
   - **mu8SceneIndex**: Is a count that increments depending on what sensor it is. I wouldn't recommend changing this.
   - **mu8AbsorbtionLevel**: How much the sensor will move for a given velocity. The higher it is, the more it will move.
   - **mau8NextBoundarySensor**: Control which sensor will prevent the current sensor from moving when they collide.

3. **Repack Bundles**  
   Once editing is done, use YAP to repack the modified bundles:
   ```bash
   YAP c <input folder> <output bundle>
   ```
   (More details in the [YAP README](https://github.com/burninrubber0/YAP/tree/directory?tab=readme-ov-file#extracting-multiple-bundles))

4. **Install Files**  
   Replace the original files with the newly repacked bundles.

## Examples
![image](https://github.com/user-attachments/assets/ad0eb14f-93b4-4eb5-967d-c95c1c46b14c)
*The editor and 2x sensor direction values for the Annihilator*

![image](https://github.com/user-attachments/assets/afa156c7-219d-4039-b5ac-8e7e8115126d)  
*2x deformation on the Annihilator*



## ❗ Important Notes
- YAP handles the actual bundle extraction/repacking process
- The editor only modifies values in extracted StreamedDeformationSpecs files