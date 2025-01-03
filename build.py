import os
import sys
import shutil
import subprocess

def install_requirements():
    print("Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    # Install PyInstaller if not already installed
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_exe():
    print("Building executable...")
    
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # PyInstaller command with all necessary zeroconf imports
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--icon=logo.ico",
        "--add-data=logo.ico;.",
        "--name=XNull Remote Keys Server",
        "--add-data=requirements.txt;.",
        "--hidden-import=zeroconf",
        "--hidden-import=zeroconf._utils.ipaddress",
        "--hidden-import=zeroconf._services.info",
        "--hidden-import=zeroconf._listener",
        "--hidden-import=zeroconf._core",
        "--hidden-import=zeroconf._engine",
        "--hidden-import=zeroconf._handlers",
        "--hidden-import=zeroconf._handlers.answers",
        "--hidden-import=zeroconf._handlers.browser",
        "--hidden-import=zeroconf._handlers.query",
        "--hidden-import=zeroconf._handlers.record_manager",
        "--hidden-import=zeroconf._handlers.update",
        "--hidden-import=zeroconf._protocol.incoming",
        "--hidden-import=zeroconf._protocol.outgoing",
        "--hidden-import=zeroconf._services.browser",
        "--hidden-import=zeroconf._services.registry",
        "--hidden-import=zeroconf._utils.name",
        "--hidden-import=zeroconf._utils.time",
        "main.py"
    ]
    
    subprocess.check_call(cmd)
    
    print("\nBuild complete! Executable is in the 'dist' folder.")

if __name__ == "__main__":
    try:
        install_requirements()
        build_exe()
    except Exception as e:
        print(f"Error during build: {str(e)}")
        sys.exit(1) 