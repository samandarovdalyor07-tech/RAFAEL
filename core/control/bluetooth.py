"""
RAFAEL - Bluetooth Controller
Windows Bluetooth qurilmalarini boshqaradi.
"""

import subprocess, time, os
from core.utils.logger import get_logger

logger = get_logger(__name__)


def _ps(cmd: str) -> str:
    """PowerShell buyrug'i bajaradi"""
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True, text=True, timeout=15,
            encoding="utf-8", errors="replace"
        )
        return (r.stdout + r.stderr).strip()
    except Exception as e:
        return str(e)


class BluetoothController:

    def open_settings(self) -> str:
        """Bluetooth sozlamalarini ochadi"""
        subprocess.Popen("start ms-settings:bluetooth", shell=True)
        return "Bluetooth sozlamalari ochildi."

    def get_devices(self) -> list[str]:
        """Juftlashtirilgan qurilmalar ro'yxati"""
        out = _ps("Get-PnpDevice -Class Bluetooth | Select-Object -ExpandProperty FriendlyName")
        devices = [d.strip() for d in out.splitlines() if d.strip()]
        return devices

    def connect_device(self, device_name: str) -> str:
        """Qurilmaga ulanadi (juftlashtirilgan bo'lishi kerak).

        disconnect_device Disable-PnpDevice ishlatgani kabi, bu yerda ham
        Enable-PnpDevice bilan haqiqiy ulanish urinilinadi (avval faqat
        qurilma nomi topilgan-topilmaganini tekshirib, hech narsa ulamas edi).
        """
        logger.info(f"Bluetooth ulanish: {device_name}")

        ps = f"""
$dev = Get-PnpDevice -Class Bluetooth | Where-Object {{ $_.FriendlyName -like '*{device_name}*' }} | Select-Object -First 1
if (-not $dev) {{
    Write-Output 'NOT_FOUND'
}} else {{
    if ($dev.Status -ne 'OK') {{
        Enable-PnpDevice -InstanceId $dev.InstanceId -Confirm:$false -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 800
        $dev = Get-PnpDevice -InstanceId $dev.InstanceId
    }}
    Write-Output "$($dev.FriendlyName)|$($dev.Status)"
}}
"""
        result = _ps(ps).strip()

        if "NOT_FOUND" in result or not result:
            self.open_settings()
            return f"{device_name} juftlashtirilgan qurilmalar orasida topilmadi. Bluetooth sozlamalari ochildi — qo'lda ulang."

        found_name, _, status = result.rpartition("|")
        found_name = found_name or device_name

        if status == "OK":
            return f"{found_name} ga ulandi."

        self.open_settings()
        return f"{found_name} topildi, lekin avtomatik ulanmadi. Bluetooth sozlamalari ochildi — qo'lda ulang."

    def disconnect_device(self, device_name: str) -> str:
        """Qurilmani uzadi"""
        ps = f"""
$dev = Get-PnpDevice | Where-Object {{ $_.FriendlyName -like '*{device_name}*' -and $_.Status -eq 'OK' }}
if ($dev) {{ Disable-PnpDevice -InstanceId $dev.InstanceId -Confirm:$false; Write-Output 'OK' }}
else {{ Write-Output 'NOT_FOUND' }}
"""
        result = _ps(ps)
        if "OK" in result:
            return f"{device_name} uzildi."
        return f"{device_name} topilmadi."

    def list_devices(self) -> str:
        """Ulangan qurilmalar ro'yxatini qaytaradi"""
        ps = "Get-PnpDevice -Class Bluetooth | Where-Object {$_.Status -eq 'OK'} | Select-Object -ExpandProperty FriendlyName"
        result = _ps(ps)
        devices = [d for d in result.splitlines() if d.strip()]
        if devices:
            return "Ulangan qurilmalar: " + ", ".join(devices[:5])
        return "Hozir ulangan Bluetooth qurilma yo'q."
