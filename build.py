"""
build.py — Genera MonitorToggle.exe con PyInstaller
Ejecutar en Windows:  python build.py
"""
import subprocess
import sys

subprocess.run([
    sys.executable, "-m", "pip", "install", "pyinstaller", "pystray", "pillow"
], check=True)

subprocess.run([
    "pyinstaller",
    "--onefile",
    "--windowed",                   # sin consola
    "--name", "MonitorToggle",
    "--icon", "NONE",               # puedes poner un .ico aquí
    "monitor_tray.py",
], check=True)

print("\n✅ Listo. El ejecutable está en dist/MonitorToggle.exe")
print("Para que arranque con Windows, crea un acceso directo en:")
print(r"  %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
