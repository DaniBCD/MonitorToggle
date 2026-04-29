@echo off
setlocal enabledelayedexpansion
title MonitorToggle - Instalador

echo.
echo  +------------------------------------------+
echo  ^|      MonitorToggle - Instalador          ^|
echo  +------------------------------------------+
echo.

:: ── 1. Verificar Python ──────────────────────────────────────────────────────
echo [1/4] Comprobando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Python no encontrado.
    echo  Descargalo desde https://www.python.org/downloads/
    echo  Marca "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  OK: %PYVER% detectado.
echo.

:: ── 2. Instalar dependencias ─────────────────────────────────────────────────
echo [2/4] Instalando dependencias (pystray, pillow, pyinstaller)...
echo.
python -m pip install --upgrade pip --quiet --no-warn-script-location
python -m pip install pystray pillow pyinstaller --quiet --no-warn-script-location
if errorlevel 1 (
    echo.
    echo  ERROR: Fallo al instalar dependencias.
    pause
    exit /b 1
)
echo  OK: Dependencias instaladas.
echo.

:: ── 3. Compilar .exe ─────────────────────────────────────────────────────────
echo [3/4] Compilando MonitorToggle.exe (puede tardar un minuto)...
echo.
set "SCRIPT_DIR=%~dp0"
set "DIST_DIR=%SCRIPT_DIR%dist"
set "BUILD_LOG=%SCRIPT_DIR%build_log.txt"

python -m PyInstaller --onefile --windowed --name MonitorToggle "%SCRIPT_DIR%monitor_tray.py" --distpath "%DIST_DIR%" --workpath "%SCRIPT_DIR%build_tmp" --specpath "%SCRIPT_DIR%build_tmp" > "%BUILD_LOG%" 2>&1
if errorlevel 1 (
    echo  ERROR: Fallo la compilacion. Revisa build_log.txt para mas detalles.
    echo.
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-Content '%BUILD_LOG%' | Select-Object -Last 15"
    echo.
    pause
    exit /b 1
)
echo  OK: Ejecutable creado en: %DIST_DIR%\MonitorToggle.exe
echo.

:: ── 4. Autoarranque ──────────────────────────────────────────────────────────
echo [4/4] Configurar autoarranque con Windows...
echo.
set /p AUTOSTART="  Arrancar automaticamente con Windows? (S/N): "
echo.

if /i "%AUTOSTART%"=="S" (
    :: Usamos un script .ps1 temporal para evitar problemas con rutas con espacios
    set "PS1=%TEMP%\mt_shortcut.ps1"
    set "TARGET=%DIST_DIR%\MonitorToggle.exe"
    set "SHORTCUT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\MonitorToggle.lnk"

    (
        echo $ws = New-Object -ComObject WScript.Shell
        echo $s = $ws.CreateShortcut^('!SHORTCUT!'^)
        echo $s.TargetPath = '!TARGET!'
        echo $s.WorkingDirectory = '!DIST_DIR!'
        echo $s.Description = 'MonitorToggle Tray App'
        echo $s.Save^(^)
    ) > "!PS1!"

    powershell -NoProfile -ExecutionPolicy Bypass -File "!PS1!"
    del "!PS1!" >nul 2>&1

    if exist "!SHORTCUT!" (
        echo  OK: Autoarranque configurado.
    ) else (
        echo  AVISO: No se pudo crear el acceso directo.
        echo  Copia dist\MonitorToggle.exe manualmente a:
        echo  %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\
    )
) else (
    echo  -- Autoarranque omitido.
)

echo.

:: ── Lanzar ahora ─────────────────────────────────────────────────────────────
set /p LAUNCH="  Lanzar MonitorToggle ahora? (S/N): "
echo.
if /i "%LAUNCH%"=="S" (
    start "" "%DIST_DIR%\MonitorToggle.exe"
    echo  OK: MonitorToggle iniciado. Busca el icono en la barra de tareas.
)

:: ── Limpieza ──────────────────────────────────────────────────────────────────
echo.
set /p CLEANUP="  Borrar archivos temporales de compilacion? (S/N): "
if /i "%CLEANUP%"=="S" (
    if exist "%SCRIPT_DIR%build_tmp" rmdir /s /q "%SCRIPT_DIR%build_tmp"
    if exist "%BUILD_LOG%" del "%BUILD_LOG%"
    echo  OK: Temporales eliminados.
)

echo.
echo  +------------------------------------------+
echo  ^|   Instalacion completada. Listo!         ^|
echo  +------------------------------------------+
echo.
echo  Para desinstalar del autoarranque, ejecuta uninstall.bat
echo.
pause
