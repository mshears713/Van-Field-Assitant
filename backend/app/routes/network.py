from fastapi import APIRouter

from ..config import config

router = APIRouter()


@router.get("/network/status")
def get_network_status() -> dict:
    return {
        "ok": True,
        "implemented": False,
        "message": (
            "Network mode switching automation is not implemented yet. "
            "Use this as a reference only. Switch Wi-Fi manually when needed."
        ),
        "current_mode": "unknown",
        "host": config.HOST,
        "port": config.PORT,
        "dashboard_url_hint": f"http://<mini-pc-ip>:{config.PORT}",
        "manual_checklist": [
            "Ensure Android phone and mini PC are on the same Wi-Fi network.",
            "Find mini PC IP: run 'ipconfig | findstr IPv4' in a Windows terminal.",
            "Open http://<mini-pc-ip>:8080 in Android browser.",
            "If phone cannot connect: check Windows Firewall allows TCP port 8080 inbound.",
            "Firewall command: netsh advfirewall firewall add rule name=\"FieldAssistant\" dir=in action=allow protocol=TCP localport=8080",
            "WARNING: Switching Wi-Fi mode on the mini PC will disconnect the Android dashboard. Reconnect manually after switching.",
        ],
        "network_modes": {
            "local_field": "Mini PC creates its own Wi-Fi network (FieldAssistantNet). Android phone connects to it. No internet.",
            "internet_sync": "Mini PC joins iPhone hotspot temporarily for downloads. Android dashboard may disconnect during this mode.",
        },
    }
