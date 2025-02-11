import customtkinter
from sensor_editor import SensorEditor

# Set appearance mode and default color theme
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue")

if __name__ == "__main__":
    root = customtkinter.CTk()
    app = SensorEditor(root)
    root.mainloop()
