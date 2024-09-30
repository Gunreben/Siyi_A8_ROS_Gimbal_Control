import tkinter as tk
from tkinter import ttk
import socket
import struct
import time

# Generate the CRC16 table using the polynomial G(X) = X^16 + X^12 + X^5 + 1 (0x1021)
def generate_crc16_table():
    crc16_tab = []
    for i in range(256):
        crc = i << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
        crc16_tab.append(crc)
    return crc16_tab

crc16_tab = generate_crc16_table()

def CRC16_cal(data: bytes, crc_init=0x0000):
    crc = crc_init
    for b in data:
        temp = (crc >> 8) & 0xFF
        index = b ^ temp
        oldcrc16 = crc16_tab[index]
        crc = ((crc << 8) ^ oldcrc16) & 0xFFFF
    return crc


class GimbalControlInterface:
    def __init__(self, master):
        self.master = master
        master.title("Gimbal Control")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.gimbal_ip = "192.168.144.25"
        self.gimbal_port = 37260

        self.last_update_time = 0
        self.update_interval = 0.1  # 100ms

        # Zoom Control
        self.zoom_frame = ttk.LabelFrame(master, text="Zoom Control")
        self.zoom_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.zoom_in_button = ttk.Button(self.zoom_frame, text="Zoom In", command=self.zoom_in)
        self.zoom_in_button.grid(row=0, column=0, padx=5, pady=5)

        self.zoom_out_button = ttk.Button(self.zoom_frame, text="Zoom Out", command=self.zoom_out)
        self.zoom_out_button.grid(row=0, column=1, padx=5, pady=5)

        # Gimbal Rotation Control
        self.rotation_frame = ttk.LabelFrame(master, text="Gimbal Rotation")
        self.rotation_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.yaw_label = ttk.Label(self.rotation_frame, text="Yaw:")
        self.yaw_label.grid(row=0, column=0, padx=5, pady=5)
        self.yaw_slider = ttk.Scale(self.rotation_frame, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.slider_moved)
        self.yaw_slider.grid(row=0, column=1, padx=5, pady=5)

        self.pitch_label = ttk.Label(self.rotation_frame, text="Pitch:")
        self.pitch_label.grid(row=1, column=0, padx=5, pady=5)
        self.pitch_slider = ttk.Scale(self.rotation_frame, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.slider_moved)
        self.pitch_slider.grid(row=1, column=1, padx=5, pady=5)

        # Status Label
        self.status_label = ttk.Label(master, text="Ready")
        self.status_label.grid(row=2, column=0, padx=10, pady=10)

        self.start_rotation_updates()

    def zoom_in(self):
        command = b"\x55\x66\x01\x01\x00\x00\x00\x05\x01\x8d\x64"
        self.send_command(command)

    def zoom_out(self):
        command = b"\x55\x66\x01\x01\x00\x00\x00\x05\xFF\x5c\x6a"
        self.send_command(command)

    def slider_moved(self, event=None):
        self.update_rotation()

    def update_rotation(self):
        current_time = time.time()
        if current_time - self.last_update_time >= self.update_interval:
            yaw = int(self.yaw_slider.get())
            pitch = int(self.pitch_slider.get())
            
            # Ensure values are in the -100 to 100 range
            yaw = max(-100, min(100, yaw))
            pitch = max(-100, min(100, pitch))
            
            # Create the command without CRC
            command = struct.pack('>BBHHHBB', 0x55, 0x66, 0x01, 0x02, 0x00, 0x07, yaw & 0xFF, pitch & 0xFF)
            
            # Calculate CRC
            crc = CRC16_cal(command)

            # Append the CRC16 checksum at the end of the data
            # Choose the desired endianess for the CRC (here, big-endian is used)
            command = command + struct.pack('>H', crc)  # Append CRC in big-endian format
            
            self.send_command(command)
            self.last_update_time = current_time
        
        # Schedule the next update
        self.master.after(int(self.update_interval * 1000), self.update_rotation)

    def send_command(self, command):
        try:
            self.sock.sendto(command, (self.gimbal_ip, self.gimbal_port))
            self.status_label.config(text="Command sent successfully")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")

    def start_rotation_updates(self):
        self.update_rotation()

if __name__ == "__main__":
    root = tk.Tk()
    app = GimbalControlInterface(root)
    root.mainloop()