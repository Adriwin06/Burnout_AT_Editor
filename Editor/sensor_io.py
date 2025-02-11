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
                packed = struct.pack(
                    SENSOR_STRUCT_FORMAT,
                    *sensor["maDirectionParams"],
                    sensor["mfRadius"],
                    *sensor["maNextSensor"],
                    sensor["mu8SceneIndex"],
                    sensor["mu8AbsorbtionLevel"],
                    *sensor["mau8NextBoundarySensor"]
                )
                padding = sensor.get("padding", b"\x00" * (SENSOR_STEP - SENSOR_FIELDS_SIZE))
                f.write(packed + padding)
        return True
    except Exception as e:
        print(f"Error writing file {filepath}: {e}")
        return False
