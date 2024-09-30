import tkinter as tk
from tkinter import ttk
import socket

class GimbalControlInterface:
    def __init__(self, master):
        self.master = master
        master.title("Gimbal Control")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.gimbal_ip = "192.168.144.25"
        self.gimbal_port = 37260

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
        self.yaw_slider = ttk.Scale(self.rotation_frame, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.update_rotation)
        self.yaw_slider.grid(row=0, column=1, padx=5, pady=5)

        self.pitch_label = ttk.Label(self.rotation_frame, text="Pitch:")
        self.pitch_label.grid(row=1, column=0, padx=5, pady=5)
        self.pitch_slider = ttk.Scale(self.rotation_frame, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.update_rotation)
        self.pitch_slider.grid(row=1, column=1, padx=5, pady=5)

        # Status Label
        self.status_label = ttk.Label(master, text="Ready")
        self.status_label.grid(row=2, column=0, padx=10, pady=10)

    def zoom_in(self):
        command = b"\x55\x66\x01\x01\x00\x00\x00\x05\x01\x8d\x64"
        self.send_command(command)

    def zoom_out(self):
        command = b"\x55\x66\x01\x01\x00\x00\x00\x05\xFF\x5c\x6a"
        self.send_command(command)

    def update_rotation(self, event=None):
        yaw = int(self.yaw_slider.get())
        pitch = int(self.pitch_slider.get())
        command = b"\x55\x66\x01\x02\x00\x00\x00\x07" + bytes([yaw & 0xFF, pitch & 0xFF]) + b"\x00\x00"
        self.send_command(command)

    def send_command(self, command):
        try:
            self.sock.sendto(command, (self.gimbal_ip, self.gimbal_port))
            self.status_label.config(text="Command sent successfully")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GimbalControlInterface(root)
    root.mainloop()