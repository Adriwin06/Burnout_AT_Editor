import struct

# Global constants
START_OFFSET = 0x120
SENSOR_STEP = 0x40
NUM_SENSORS = 20

# Sensor fields occupy 38 bytes:
SENSOR_FIELDS_SIZE = 38
SENSOR_STRUCT_FORMAT = ">6ff6BBB2B"

SENSOR_POSITIONS = [
    "Roof Upper Left", "Roof Upper Right", "Roof Lower Right", "Roof Lower Left", "Front Lower Right",
    "Front Upper Right", "Front Lower Middle", "Front Upper Middle", "Front Lower Left", "Front Upper Left",
    "Door Rear Left", "Door Front Left", "Door Rear Right", "Door Front Right", "Rear Lower Right", 
    "Rear Upper Right", "Rear Lower Middle", "Rear Upper Middle", "Rear Lower Left", "Rear Upper Left"
]

def read_sensor_data(filepath):
    sensors = []
    try:
        with open(filepath, "rb") as f:
            for i in range(NUM_SENSORS):
                offset = START_OFFSET + i * SENSOR_STEP
                f.seek(offset)
                data = f.read(SENSOR_STEP)
                if len(data) < SENSOR_STEP:
                    raise ValueError("Unexpected end of file")
                sensor_data = data[:SENSOR_FIELDS_SIZE]
                padding = data[SENSOR_FIELDS_SIZE:]
                unpacked = struct.unpack(SENSOR_STRUCT_FORMAT, sensor_data)
                sensor = {
                    "maDirectionParams": unpacked[0:6],
                    "mfRadius": unpacked[6],
                    "maNextSensor": unpacked[7:13],
                    "mu8SceneIndex": unpacked[13],
                    "mu8AbsorbtionLevel": unpacked[14],
                    "mau8NextBoundarySensor": unpacked[15:17],
                    "padding": padding
                }
                sensors.append(sensor)
        return sensors
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None

def write_sensor_data(filepath, sensors):
    try:
        with open(filepath, "r+b") as f:
            for i, sensor in enumerate(sensors):
                offset = START_OFFSET + i * SENSOR_STEP
                f.seek(offset)
                
                # Read existing sensor data to preserve unchanged values
                data = f.read(SENSOR_STEP)
                if len(data) < SENSOR_STEP:
                    raise ValueError("Unexpected end of file")
                
                # Unpack the existing sensor data
                unpacked = struct.unpack(SENSOR_STRUCT_FORMAT, data[:SENSOR_FIELDS_SIZE])
                
                # Preserve original values
                updated_sensor = {
                    "maDirectionParams": sensor.get("maDirectionParams", unpacked[0:6]),
                    "mfRadius": sensor.get("mfRadius", unpacked[6]),
                    "maNextSensor": sensor.get("maNextSensor", unpacked[7:13]),
                    "mu8SceneIndex": sensor.get("mu8SceneIndex", unpacked[13]),
                    "mu8AbsorbtionLevel": sensor.get("mu8AbsorbtionLevel", unpacked[14]),
                    "mau8NextBoundarySensor": sensor.get("mau8NextBoundarySensor", unpacked[15:17]),
                }

                # Pack the updated values
                packed = struct.pack(
                    SENSOR_STRUCT_FORMAT,
                    *updated_sensor["maDirectionParams"],
                    updated_sensor["mfRadius"],
                    *updated_sensor["maNextSensor"],
                    updated_sensor["mu8SceneIndex"],
                    updated_sensor["mu8AbsorbtionLevel"],
                    *updated_sensor["mau8NextBoundarySensor"]
                )

                # Preserve original padding
                padding = data[SENSOR_FIELDS_SIZE:]

                # Seek and write the corrected data
                f.seek(offset)
                f.write(packed + padding)

        return True
    except Exception as e:
        print(f"Error writing file {filepath}: {e}")
        return False
