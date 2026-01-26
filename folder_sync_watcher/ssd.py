from typing import Optional

import win32api


def find_ssd_drive_letter(volume_label: str) -> Optional[str]:
    drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]
    for drive in drives:
        try:
            current_label = win32api.GetVolumeInformation(drive)[0].strip()
            if current_label.lower() == volume_label.lower().strip():
                return drive.rstrip('\\')
        except Exception:
            continue
    return None
