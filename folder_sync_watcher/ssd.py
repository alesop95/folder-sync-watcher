from typing import Optional

try:
    import win32api
except Exception:  # pragma: no cover
    win32api = None


def find_ssd_drive_letter(volume_label: str) -> Optional[str]:
    if win32api is None:
        return None
    drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]
    for drive in drives:
        try:
            current_label = win32api.GetVolumeInformation(drive)[0].strip()
            if current_label.lower() == volume_label.lower().strip():
                return drive.rstrip('\\')
        except Exception:
            continue
    return None
