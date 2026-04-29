@echo off
title MonitorToggle - Desinstalador

echo.
echo  +------------------------------------------+
echo  ^|     MonitorToggle - Desinstalador        ^|
echo  +------------------------------------------+
echo.

taskkill /f /im MonitorToggle.exe >nul 2>&1
echo  OK: Proceso detenido (si estaba activo).

set "SHORTCUT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\MonitorToggle.lnk"
if exist "%SHORTCUT%" (
    del "%SHORTCUT%"
    echo  OK: Autoarranque eliminado.
) else (
    echo  -- No habia acceso directo de autoarranque.
)

echo.
echo  +------------------------------------------+
echo  ^|      Desinstalacion completada.          ^|
echo  +------------------------------------------+
echo.
pause
