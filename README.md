# MonitorToggle 🖥️↔️🖥️

Pequeña app que vive en la **system tray** de Windows y alterna entre 1 y 2 monitores con un clic.

## Características

- **Click izquierdo** o menú → alterna el modo
- **1 monitor → 2**: activa el segundo monitor en modo "extender"
- **2 monitores → 1**: apaga el monitor donde NO está el cursor
  - Si el cursor está en el monitor **primario** → `DisplaySwitch /internal`
  - Si el cursor está en un monitor **secundario** → `DisplaySwitch /external`
- Icono en la tray cambia visualmente según el modo activo
- Tooltip informativo en hover

## 🚀 Descarga e Instalación

1. Ve a la pestaña de [**Releases**](../../releases/latest) en GitHub.
2. Descarga el archivo `MonitorToggle.exe` de la última versión.
3. Colócalo en la carpeta que prefieras y ejecútalo.

### Autoarranque con Windows

Si quieres que se inicie automáticamente al encender el PC:
1. Crea un acceso directo de `MonitorToggle.exe`.
2. Presiona `Win + R`, escribe `shell:startup` y presiona Enter.
3. Mueve el acceso directo a esa carpeta.

---

## 🛠️ Desarrollo / Compilación manual

### Requisitos
- Windows 10/11
- Python 3.10+

### Construir desde el código fuente
1. Clona este repositorio: `git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git`
2. Ejecuta `install.bat`. Este script automáticamente:
   - Instalará las dependencias necesarias (`pystray`, `pillow`, `pyinstaller`).
   - Compilará el ejecutable.
   - Te preguntará si quieres configurar el autoarranque.

También puedes desinstalar el autoarranque en cualquier momento ejecutando `uninstall.bat`.

## Cómo funciona

Usa `DisplaySwitch.exe` (integrado en Windows) para cambiar el modo de pantalla — la misma herramienta que usa `Win + P`. No necesita drivers ni librerías externas en runtime.

La detección del monitor activo usa `GetCursorPos` + `MonitorFromPoint` de la Win32 API para saber exactamente en qué monitor estás cuando haces clic.
