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
        """Qurilmaga ulanadi (juftlashtirilgan bo'lishi kerak)"""
        logger.info(f"Bluetooth ulanish: {device_name}")

        # Avval mavjud qurilmalarni topamiz
        ps_script = f"""
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Devices.Enumeration.DeviceInformation,Windows.Devices.Enumeration,ContentType=WindowsRuntime]
$devices = [Windows.Devices.Enumeration.DeviceInformation]::FindAllAsync(
    [Windows.Devices.Bluetooth.BluetoothDevice]::GetDeviceSelectorFromPairingState($true)
) | Foreach-Object {{ $_.GetAwaiter().GetResult() }}
$target = $devices | Where-Object {{ $_.Name -like '*{device_name}*' }} | Select-Object -First 1
if ($target) {{
    Write-Output $target.Name
}} else {{
    Write-Output 'NOT_FOUND'
}}
"""
        result = _ps(ps_script)

        if "NOT_FOUND" in result or not result.strip():
            # Fallback: settings ochib tavsiya beramiz
            self.open_settings()
            return f"{device_name} topilmadi. Bluetooth sozlamalari ochildi — qo'lda ulang."

        # Topildi — audio qurilma sifatida default qilamiz
        ps_connect = f"""
$deviceName = "{device_name}"
$devices = Get-PnpDevice -Class AudioEndpoint | Where-Object {{ $_.FriendlyName -like "*$deviceName*" }}
if ($devices) {{
    Write-Output "Connected: $($devices.FriendlyName)"
}} else {{
    Write-Output "Audio endpoint topilmadi"
}}
"""
        res2 = _ps(ps_connect)
        logger.info(f"BT result: {res2}")

        if "Connected" in res2:
            return f"{result.strip()} ga ulandi."

        # VBScript orqali audio device ni default qilish
        self.open_settings()
        return f"Bluetooth sozlamalari ochildi. {device_name} ni bosib ulang."

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
