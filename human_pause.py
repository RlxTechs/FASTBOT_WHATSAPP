import ctypes
import time

_last_print = 0

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("dwTime", ctypes.c_uint)
    ]

def get_idle_seconds() -> float:
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)

    if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
        return 9999

    millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
    return max(0, millis / 1000.0)

def should_pause_for_human(settings) -> bool:
    global _last_print

    if not bool(settings.get("pause_when_user_active", True)):
        return False

    idle_needed = float(settings.get("resume_after_user_idle_seconds", 5))
    idle = get_idle_seconds()

    if idle < idle_needed:
        now = time.time()
        if now - _last_print > 2:
            print(f"⏸️ Pause humaine : activité souris/clavier détectée. Reprise après {idle_needed}s d'inactivité. Idle={idle:.1f}s")
            _last_print = now
        return True

    return False
