"""
Monitor Toggle Tray App
-----------------------
Vive en la system tray de Windows.
Click izquierdo o menú → alterna entre 1 monitor y 2 monitores.
En modo 1 monitor, usa siempre el monitor desde el que se hizo clic.
"""

import sys
import subprocess
import ctypes
import ctypes.wintypes
import threading
import os
from PIL import Image, ImageDraw, ImageFont
import pystray


# ── DisplaySwitch wrapper ────────────────────────────────────────────────────

def get_monitor_count() -> int:
    """Devuelve el número de monitores activos actualmente."""
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(80)  # SM_CMONITORS = 80


def set_display_mode(mode: str):
    """
    mode: 'extend'  → 2 monitores (extender)
          'internal' → solo monitor principal
          'external' → solo monitor secundario
          'clone'    → duplicar
    Usa DisplaySwitch.exe, que es la forma limpia en Windows.
    """
    modes = {
        "extend":   "/extend",
        "internal": "/internal",
        "external": "/external",
        "clone":    "/clone",
    }
    arg = modes.get(mode)
    if arg:
        subprocess.Popen(["DisplaySwitch.exe", arg],
                         creationflags=subprocess.CREATE_NO_WINDOW)


def get_cursor_monitor() -> int:
    """
    Devuelve el índice del monitor donde está el cursor (0 = primario, 1 = secundario…).
    Usa MonitorFromPoint para identificar el monitor exacto.
    """
    user32 = ctypes.windll.user32

    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))

    # MONITOR_DEFAULTTONEAREST = 2
    hmonitor = user32.MonitorFromPoint(pt, 2)

    # Enumeramos monitores para saber si el cursor está en el primario o secundario
    monitors = []

    MonitorEnumProc = ctypes.WINFUNCTYPE(
        ctypes.c_bool,
        ctypes.c_ulong,
        ctypes.c_ulong,
        ctypes.POINTER(ctypes.wintypes.RECT),
        ctypes.c_double,
    )

    def callback(hMon, hdcMon, lprcMonitor, dwData):
        monitors.append(hMon)
        return True

    user32.EnumDisplayMonitors(None, None, MonitorEnumProc(callback), 0)

    try:
        return monitors.index(hmonitor)
    except ValueError:
        return 0


# ── Estado global ────────────────────────────────────────────────────────────

class AppState:
    def __init__(self):
        self.is_dual = get_monitor_count() > 1
        self.icon: pystray.Icon | None = None

    def toggle(self):
        if self.is_dual:
            self._switch_to_single()
        else:
            self._switch_to_dual()

    def _switch_to_single(self):
        """Apaga el monitor que NO tiene el cursor."""
        monitor_idx = get_cursor_monitor()
        if monitor_idx == 0:
            # El cursor está en el monitor primario → apagar el secundario
            set_display_mode("internal")
        else:
            # El cursor está en un monitor secundario → convertirlo en principal
            set_display_mode("external")
        self.is_dual = False
        self._refresh_icon()

    def _switch_to_dual(self):
        set_display_mode("extend")
        self.is_dual = True
        self._refresh_icon()

    def _refresh_icon(self):
        if self.icon:
            self.icon.icon = make_icon(self.is_dual)
            self.icon.title = tooltip_text(self.is_dual)


state = AppState()


# ── Iconos generados con Pillow ──────────────────────────────────────────────

SIZE = 64
BG_ALPHA = 0  # transparente


def make_icon(dual: bool) -> Image.Image:
    """
    Dibuja un icono minimalista:
    - Dual: dos rectángulos lado a lado (verde lima)
    - Single: un rectángulo centrado (blanco/gris)
    """
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    border = 3
    gap = 4
    h_pad = 6
    v_pad = 10

    if dual:
        color = (180, 255, 60, 255)       # verde lima
        mid = SIZE // 2
        # monitor izquierdo
        draw.rounded_rectangle(
            [h_pad, v_pad, mid - gap // 2, SIZE - v_pad],
            radius=3, outline=color, width=border
        )
        # monitor derecho
        draw.rounded_rectangle(
            [mid + gap // 2, v_pad, SIZE - h_pad, SIZE - v_pad],
            radius=3, outline=color, width=border
        )
        # pie izquierdo
        lx = (h_pad + mid - gap // 2) // 2
        draw.rectangle([lx - 2, SIZE - v_pad, lx + 2, SIZE - v_pad + 3], fill=color)
        # pie derecho
        rx = (mid + gap // 2 + SIZE - h_pad) // 2
        draw.rectangle([rx - 2, SIZE - v_pad, rx + 2, SIZE - v_pad + 3], fill=color)
    else:
        color = (220, 220, 220, 255)      # blanco suave
        w = SIZE - h_pad * 4
        x0 = (SIZE - w) // 2
        draw.rounded_rectangle(
            [x0, v_pad, x0 + w, SIZE - v_pad],
            radius=3, outline=color, width=border
        )
        cx = SIZE // 2
        draw.rectangle([cx - 2, SIZE - v_pad, cx + 2, SIZE - v_pad + 3], fill=color)

    return img


def tooltip_text(dual: bool) -> str:
    return "Monitor Toggle — Dual (clic para 1 monitor)" if dual else "Monitor Toggle — Single (clic para 2 monitores)"


# ── Menú y callbacks ─────────────────────────────────────────────────────────

def on_toggle(icon, item):
    threading.Thread(target=state.toggle, daemon=True).start()


def on_quit(icon, item):
    icon.stop()


def on_click(icon, button, pressed):
    """Click izquierdo también alterna."""
    if pressed and button == pystray.mouse.Button.left:
        threading.Thread(target=state.toggle, daemon=True).start()


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    menu = pystray.Menu(
        pystray.MenuItem(
            lambda item: "Cambiar a 2 monitores" if state.is_dual else "Cambiar a 1 monitor",
            on_toggle,
            default=True,
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Salir", on_quit),
    )

    icon = pystray.Icon(
        name="MonitorToggle",
        icon=make_icon(state.is_dual),
        title=tooltip_text(state.is_dual),
        menu=menu,
    )
    icon.on_click = on_click  # click izquierdo
    state.icon = icon
    icon.run()


if __name__ == "__main__":
    main()
