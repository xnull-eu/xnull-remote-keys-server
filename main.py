import sys
import os
import socket
import threading
import keyboard
import websockets
import asyncio
import tkinter as tk
from tkinter import ttk
import pystray
from PIL import Image
from pystray import MenuItem as item
from zeroconf import ServiceInfo, Zeroconf
import win32api
import win32con

class RemoteKeyServer:
    def __init__(self):
        self.port = 8765
        self.zeroconf = None
        self.running = False
        self.setup_gui()
        self.setup_tray()
        
    def setup_gui(self):
        self.window = tk.Tk()
        self.window.title("XNull Remote Keys Server")
        self.window.geometry("300x150")
        
        # Set window icon
        try:
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, 'logo.ico')
            else:
                icon_path = 'logo.ico'
            self.window.iconbitmap(icon_path)
        except Exception:
            pass

        # Intercept minimize button
        self.window.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.window.bind("<Unmap>", lambda e: self.handle_minimize() if self.window.state() == 'iconic' else None)
        
        # Status label
        self.status_label = ttk.Label(
            self.window, 
            text="Server Status: Stopped", 
            foreground="red",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=20)
        
        # Connection status label
        self.connection_label = ttk.Label(
            self.window, 
            text="No client connected", 
            foreground="gray",
            font=("Arial", 10)
        )
        self.connection_label.pack(pady=10)
        
        # Start/Stop button
        self.toggle_button = ttk.Button(
            self.window, 
            text="Start Server", 
            command=self.toggle_server
        )
        self.toggle_button.pack(pady=10)
        
    def setup_tray(self):
        # Create system tray icon
        try:
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, 'logo.ico')
            else:
                icon_path = 'logo.ico'
            image = Image.open(icon_path)
        except Exception:
            # Create a simple colored square if icon fails to load
            image = Image.new('RGB', (64, 64), color='blue')

        menu = (
            item('Show', self.show_window),
            item('Exit', self.on_closing)
        )
        
        self.tray_icon = pystray.Icon("XNull Remote Keys", image, "XNull Remote Keys Server", menu)
        
        # Start system tray icon in a separate thread
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self):
        self.window.deiconify()
        self.window.state('normal')
        self.window.focus_force()

    def hide_window(self):
        self.window.withdraw()
        
    def handle_minimize(self):
        self.window.withdraw()
        self.tray_icon.notify(
            "Application Minimized",
            "XNull Remote Keys Server is still running in the background"
        )
        
    def toggle_server(self):
        if not self.running:
            self.start_server()
            self.toggle_button.config(text="Stop Server")
            self.status_label.config(
                text="Server Status: Running",
                foreground="green"
            )
            self.connection_label.config(
                text="Waiting for client...",
                foreground="orange"
            )
        else:
            self.stop_server()
            self.toggle_button.config(text="Start Server")
            self.status_label.config(
                text="Server Status: Stopped",
                foreground="red"
            )
            self.connection_label.config(
                text="No client connected",
                foreground="gray"
            )

    async def handle_client(self, websocket, path):
        try:
            self.window.after(0, lambda: self.connection_label.config(
                text="Client connected",
                foreground="green"
            ))
            async for message in websocket:
                key = message.strip()
                if key.startswith("NUM_"):
                    key = key.replace("NUM_", "")
                    try:
                        numpad_map = {
                            "0": win32con.VK_NUMPAD0,
                            "1": win32con.VK_NUMPAD1,
                            "2": win32con.VK_NUMPAD2,
                            "3": win32con.VK_NUMPAD3,
                            "4": win32con.VK_NUMPAD4,
                            "5": win32con.VK_NUMPAD5,
                            "6": win32con.VK_NUMPAD6,
                            "7": win32con.VK_NUMPAD7,
                            "8": win32con.VK_NUMPAD8,
                            "9": win32con.VK_NUMPAD9,
                            "DOT": win32con.VK_DECIMAL,
                            "ENTER": win32con.VK_RETURN
                        }
                        if key in numpad_map:
                            vk_code = numpad_map[key]
                            win32api.keybd_event(vk_code, 0, 0, 0)
                            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
                    except Exception:
                        try:
                            if key.isdigit():
                                keyboard.write(key)
                            elif key == "DOT":
                                keyboard.write(".")
                            elif key == "ENTER":
                                keyboard.press_and_release("enter")
                        except:
                            pass
                else:
                    keyboard.press_and_release(key.lower())
                
        except websockets.exceptions.ConnectionClosed:
            self.window.after(0, lambda: self.connection_label.config(
                text="Client disconnected",
                foreground="red"
            ))
        except Exception:
            pass

    def start_server(self):
        try:
            self.running = True
            self.zeroconf = Zeroconf()
            self.register_service()
            self.server_thread = threading.Thread(target=self.run_server)
            self.server_thread.daemon = True
            self.server_thread.start()
        except Exception:
            self.stop_server()
        
    def stop_server(self):
        self.running = False
        self.cleanup()
        
    def register_service(self):
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            info = ServiceInfo(
                "_remotekeys._tcp.local.",
                f"XNull Remote Keys Server on {hostname}._remotekeys._tcp.local.",
                addresses=[socket.inet_aton(local_ip)],
                port=self.port,
                properties={},
                server=f"{hostname}.local."
            )
            
            self.zeroconf.register_service(info)
        except Exception:
            raise

    def run_server(self):
        async def start():
            try:
                async with websockets.serve(self.handle_client, "0.0.0.0", self.port):
                    while self.running:
                        await asyncio.sleep(1)
            except Exception:
                pass
                    
        asyncio.run(start())

    def cleanup(self):
        try:
            if self.zeroconf:
                self.zeroconf.unregister_all_services()
                self.zeroconf.close()
                self.zeroconf = None
        except Exception:
            pass
        
    def on_closing(self):
        if self.running:
            self.stop_server()
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        self.window.destroy()
        sys.exit(0)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    server = RemoteKeyServer()
    server.run() 