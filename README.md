# XNull Remote Keys Server

A Windows application that allows you to control your computer's numpad and function keys remotely using an Android device.

## Features

- Remote numpad control
- Function keys (F1-F12) support
- System tray integration
- Auto-discovery of devices on the local network
- Minimalistic GUI interface

## Requirements

- Windows OS
- Python 3.8 or higher
- Required Python packages (installed automatically):
  - websockets
  - keyboard
  - zeroconf
  - pywin32
  - pillow
  - pystray

## Installation

1. Clone the repository:
```
git clone https://github.com/xnull-eu/xnull-remote-keys-server.git
cd xnull-remote-keys-server
```
2. Install requirements:
```
pip install -r requirements.txt
```

## Usage

1. Run the server:
```
python main.py
```
2. The server will appear in your system tray
3. Use the Android companion app to connect to this server
4. The server can be minimized to tray and will continue running in the background

## Building Executable

To create a standalone executable:
```
python build.py
```
The executable will be created in the `dist` folder.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [xnull-remote-keys](https://github.com/xnull-eu/xnull-remote-keys) - The Android client for this Windows server
